"""
Solver / simulation helpers.

This module provides a tree-based exhaustive search to find the minimal
number of moves required to reach a target number of finished owls.

The search operates over abstract game states (owl positions) and uses the
existing board path layout from a `Board` instance. It does not use the
`Deck` or players; instead it treats each possible color play (excluding
ANY and SUN) and every owl as a possible move. BFS is used to guarantee the
first time we reach the target is the minimal number of moves.
"""
from collections import deque
import time
from typing import Iterable, Optional, Tuple

from board import CardColors


def _apply_move(positions: Tuple[int, ...], owl_idx: int, color_positions: Iterable[int],
                goal_position: int) -> Optional[Tuple[int, ...]]:
    """Return a new positions tuple after moving owl `owl_idx` using a card
    whose path positions are `color_positions`.

    Follows the same rules as `Board.advance`:
    - find the next position in color_positions strictly greater than current
      owl position
    - if that position == goal_position then the owl finishes (multiple
      owls may finish on the goal)
    - otherwise skip positions occupied by other owls
    - if no valid advancement exists the state is unchanged (return None)
    """
    pos_list = list(positions)
    current_position = pos_list[owl_idx]
    new_position = current_position
    for position in color_positions:
        if position <= current_position:
            continue
        if position == goal_position:
            new_position = position
            break
        # check occupancy (other than the moving owl)
        occupied = False
        for j, p in enumerate(pos_list):
            if j == owl_idx:
                continue
            if p == position:
                occupied = True
                break
        if occupied:
            continue
        new_position = position
        break

    if new_position == current_position:
        return None
    pos_list[owl_idx] = new_position
    return tuple(pos_list)


def min_moves_with_deck(board, deck, target_finished: Optional[int] = None,
                        max_depth: Optional[int] = None, rules=None,
                        progress_interval: int = 0,
                        verbose: bool = False) -> Optional[int]:
    """BFS search that includes deck and hand state.

    State includes:
      - positions: tuple of owl positions
      - deck_index: next index in deck._card_stack to draw
      - hand: tuple of CardColors or None for empty slots
      - sun_count: number of SUN cards played so far

    The search consumes a card from hand each move (SUN or color). After
    consuming, the next deck card (if any) is drawn into that hand slot.

    If `rules` is not provided, attempts to read `deck._rules`.
    """
    # rules object for sun_to_fail and hand size
    if rules is None:
        rules = getattr(deck, "_rules", None)
    if rules is None:
        raise ValueError("rules must be provided either via deck or argument")

    if target_finished is None:
        target_finished = len(board.owls)

    # prepare deck card colors list for deterministic access
    try:
        deck_stack = deck._card_stack
    except Exception:
        # fallback: build from deck sequence
        deck_stack = [deck[i] for i in range(len(deck))]

    player_turn = 0
    goal = board.goal_position
    start_positions = tuple(owl.position for owl in board.owls)

    # initialize hand by drawing first N cards from deck (without mutating deck)
    hand_size = getattr(rules, "hand_size", 3)
    hand = []
    di = 0
    while len(hand) < hand_size and di < len(deck_stack):
        hand.append(deck_stack[di].color)
        di += 1
    # pad with None for empty slots
    while len(hand) < hand_size:
        hand.append(None)

    start_state = (start_positions, di, tuple(hand), 0)

    def finished_count_from_positions(positions):
        return sum(1 for p in positions if p == goal)

    if finished_count_from_positions(start_positions) >= target_finished:
        return 0

    from collections import deque
    q = deque()
    q.append((start_state, 0))
    seen = {start_state: 0}

    # progress counters for terminal status output
    processed = 0
    start_time = time.time()

    while q:
        (positions, deck_index, player_turn, hand_tuples, sun_count), depth = q.popleft()
        processed += 1
        if progress_interval and processed % progress_interval == 0:
            elapsed = time.time() - start_time
            rate = processed / elapsed if elapsed > 0 else float("inf")
            if verbose:
                print(f"[min_moves_with_deck] processed={processed} queue={len(q)} seen={len(seen)} "
                      f"depth={depth} elapsed={elapsed:.1f}s rate={rate:.1f}/s")
        if max_depth is not None and depth >= max_depth:
            continue

        player_turn = (depth) % rules.player_count
        hand_tuple = hand_tuples[player_turn]
        # for each hand slot that has a card
        for slot_idx, card_color in enumerate(hand_tuple):
            if card_color is None:
                continue

            # consume the card
            new_hand = list(hand_tuple)
            new_hand[slot_idx] = None
            new_deck_index = deck_index
            # draw to refill if possible
            if new_deck_index < len(deck_stack):
                new_hand[slot_idx] = deck_stack[new_deck_index].color
                new_deck_index += 1

            if card_color == CardColors.SUN:
                new_sun = sun_count + 1
                # if too many suns, this path is a failure -> skip
                if new_sun >= getattr(rules, "sun_to_fail", 999999):
                    continue
                new_positions = positions
                new_state = (new_positions, new_deck_index, tuple(new_hand), new_sun)
                if new_state in seen:
                    continue
                seen[new_state] = depth + 1
                q.append((new_state, depth + 1))
                continue

            # normal color card: try moving any owl
            for owl_idx in range(len(positions)):
                color_positions = board.path.get(card_color)
                if color_positions is None:
                    # no path for this color, treat as no-op card play
                    new_positions = positions
                else:
                    new_positions = _apply_move(positions, owl_idx, color_positions, goal)
                    if new_positions is None:
                        # card consumed but no movement
                        new_positions = positions

                if finished_count_from_positions(new_positions) >= target_finished:
                    return depth + 1

                new_state = (new_positions, new_deck_index, tuple(new_hand), sun_count)
                if new_state in seen:
                    continue
                seen[new_state] = depth + 1
                q.append((new_state, depth + 1))

    return None



if __name__ == "__main__":
    import board, simulation, rules
    r=rules.Rules()
    r.player_count=3
    r.number_of_owls=3
    r.number_of_suns=14
    r.card_color_multiple=6
    r.hand_size=3
    b=board.Board(r)
    d=board.Deck(r)
    d.create()
    d.shuffle(seed=123)
    print('deck_len', len(d))
    hand=[d._card_stack[i].color for i in range(min(len(d._card_stack), r.hand_size))]
    
    print('initial_hand', hand)
    res=simulation.min_moves_with_deck(b,d,target_finished=2,max_depth=200,rules=r)
    print('solver_result', res)

