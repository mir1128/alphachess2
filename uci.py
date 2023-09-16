
def create_uci_labels():
    labels_array = []
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    advisor_labels = ['d7e8', 'e8d7', 'e8f9', 'f9e8', 'd0e1', 'e1d0', 'e1f2', 'f2e1',
                      'd2e1', 'e1d2', 'e1f0', 'f0e1', 'd9e8', 'e8d9', 'e8f7', 'f7e8']
    bishop_labels = ['a2c4', 'c4a2', 'c0e2', 'e2c0', 'e2g4', 'g4e2', 'g0i2', 'i2g0',
                     'a7c9', 'c9a7', 'c5e7', 'e7c5', 'e7g9', 'g9e7', 'g5i7', 'i7g5',
                     'a2c0', 'c0a2', 'c4e2', 'e2c4', 'e2g0', 'g0e2', 'g4i2', 'i2g4',
                     'a7c5', 'c5a7', 'c9e7', 'e7c9', 'e7g5', 'g5e7', 'g9i7', 'i7g9']

    for l1 in range(9):
        for n1 in range(10):
            destinations = [(t, n1) for t in range(9)] + \
                           [(l1, t) for t in range(10)] + \
                           [(l1 + a, n1 + b) for (a, b) in
                            [(-2, -1), (-1, -2), (-2, 1), (1, -2), (2, -1), (-1, 2), (2, 1), (1, 2)]]  # 马走日
            for (l2, n2) in destinations:
                if (l1, n1) != (l2, n2) and l2 in range(9) and n2 in range(10):
                    move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                    labels_array.append(move)

    for p in advisor_labels:
        labels_array.append(p)

    for p in bishop_labels:
        labels_array.append(p)

    return labels_array


def to_uci_label(src, dst):
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    # Convert the source and destination tuples to UCI labels
    # Reverse the order of the coordinates to match the UCI format
    uci_label = letters[src[1]] + numbers[9 - src[0]] + letters[dst[1]] + numbers[9 - dst[0]]

    return uci_label


def get_probability(src, dst, policy_pred):
    # Convert the source and destination coordinates to a UCI label
    uci_label = to_uci_label(src, dst)

    # Create the UCI labels array
    # Find the index of the UCI label in the labels array
    label_index = uci_labels.index(uci_label)

    # Get the probability from the policy prediction vector
    probability = policy_pred[label_index]

    return probability


uci_labels = create_uci_labels()


def test_uci():
    assert to_uci_label((0, 4), (1, 4)) == 'e9e8', "Error in test case 1"
    assert to_uci_label((0, 0), (0, 1)) == 'a9b9', "Error in test case 2"
    assert to_uci_label((0, 1), (2, 2)) == 'b9c7', "Error in test case 3"
    assert to_uci_label((2, 1), (5, 1)) == 'b7b4', "Error in test case 4"
    assert to_uci_label((3, 0), (4, 0)) == 'a6a5', "Error in test case 5"


if __name__ == '__main__':
    test_uci()
    exit()
