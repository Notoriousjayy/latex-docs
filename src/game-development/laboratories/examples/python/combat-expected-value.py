def moments(outcomes):
    assert abs(sum(p for x, p in outcomes) - 1) < 1e-10
    mean = sum(x * p for x, p in outcomes)
    variance = sum(p * (x - mean) ** 2 for x, p in outcomes)
    return mean, variance

def test():
    a = moments([(3, .85), (0, .15)])
    b = moments([(6, .45), (0, .55)])
    assert abs(a[0] - 2.55) < 1e-10
    assert abs(b[0] - 2.70) < 1e-10
    assert b[1] > a[1]

if __name__ == "__main__":
    test()
    print("combat: ok", moments([(3, .85), (0, .15)]))
