from sage.all_cmdline import *

alphabet_size = 27
G = Permutations(alphabet_size**2)

def all_pairings_offsets(l, n_offsets):
    assert(len(l) % 2 == 0)

    if len(l) == 0:
        return [[]]

    out = []
    for i in range(1, len(l)):
        for rest in all_pairings_offsets(l[1:i] + l[i+1:], n_offsets):
            for offset in range(n_offsets):
                out.append([(l[0], l[i], offset)] + rest)
    return out

def all_pairings_offsets_subsets(l, n_offsets):
    if len(l) == 0:
        return [[]]
    elif len(l) == 1:
        return [[(l[0],)]]

    out = []
    for rest in all_pairings_offsets_subsets(l[1:], n_offsets):
        out.append([(l[0],)] + rest)
    for i in range(1, len(l)):
        for rest in all_pairings_offsets_subsets(l[1:i] + l[i+1:], n_offsets):
            for offset in range(n_offsets):
                out.append([(l[0], l[i], offset)] + rest)
    return out

def product(l, i = 1):
    if i == alphabet_size**2 + 1:
        return [[]]

    out = []
    for s in l[i]:
        for rest in product(l, i + 1):
            out.append(s + rest)
    return out

def square_roots_sage(p_sq):
    print("Cycle type:", p_sq.cycle_type())

    cycles = [[] for i in range(alphabet_size**2 + 1)]
    for cycle in p_sq.to_cycles():
        cycles[len(cycle)].append(cycle)

    assert(cycles[0] == [])

    possible_out_cycles = [[] for i in range(alphabet_size**2 + 1)]
    for l, cycles_with_len in enumerate(cycles):
        if len(cycles_with_len) == 0:
            possible_out_cycles[l] = [[]]
            continue

        if l % 2 == 0:
            pairings = all_pairings_offsets(cycles_with_len, l)
        else:
            pairings = all_pairings_offsets_subsets(cycles_with_len, l)

        for pairing in pairings:
            out_cycles = []
            for pair in pairing:
                if len(pair) == 1:
                    assert(l % 2 == 1)
                    inv2 = (l + 1) // 2
                    out_cycles.append([pair[0][(i * inv2) % l] for i in range(l)])
                else:
                    assert(len(pair) == 3)
                    out_cycle = []
                    for i in range(l):
                        out_cycle.append(pair[0][i])
                        out_cycle.append(pair[1][(i + pair[2]) % l])
                    out_cycles.append(out_cycle)
            possible_out_cycles[l].append(out_cycles)

    num_outputs = 1
    for poss in possible_out_cycles:
        num_outputs *= len(poss)
    print("Number of permutations:", num_outputs)

    return [Permutation([tuple(cyc) for cyc in cyc_set]) for cyc_set in product(possible_out_cycles)]

# p must be a list mapping integers to integers.
def square_roots(p_sq):
    assert(len(p_sq) == alphabet_size**2)
    p_sq_sage = Permutation([i + 1 for i in p_sq])
    return [[i - 1 for i in list(p)] for p in square_roots_sage(p_sq_sage)]
