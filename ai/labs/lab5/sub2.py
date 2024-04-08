import numpy as np

def forward_algorithm(observations):
    n = len(observations)
    F = np.zeros((n+3, 2))
    F[0, 0] = 0.5
    F[0, 1] = 0.5
    rainx2 = 0.7
    rainXnone = 0.3
    umbrellaXrain = 0.9
    umbrellaXnone = 0.2

    for t in range(1, n+1):
        F[t, 0] = (F[t-1, 0] * rainx2 + F[t-1, 1] * rainXnone) * umbrellaXrain if observations[t-1] == 1 else \
                  (F[t-1, 1] * (1-rainx2) + F[t-1, 0] * (1-rainXnone)) * (1-umbrellaXrain)
        F[t, 1] = (F[t-1, 0] * rainXnone + F[t-1, 1] * rainx2) * umbrellaXnone if observations[t-1] == 1 else \
                  (F[t-1, 1] * (1-rainXnone) + F[t-1, 0] * (1-rainx2)) * (1-umbrellaXnone)
    normalization_factor = np.sum(F[:n+1], axis=1)
    F[:n+1] /= normalization_factor[:, None]
    F[n+1, 0] = F[n, 0] * rainx2 + F[n, 1] * (1-rainx2)
    F[n+1, 1] = F[n, 1] * rainx2 + F[n, 0] * (1-rainx2)
    F[n+2, 0] = F[n+1, 0] * rainx2 + F[n+1, 1] * (1-rainx2)
    F[n+2, 1] = F[n+1, 1] * rainx2 + F[n+1, 0] * (1-rainx2)
    normalization_factor = np.sum(F, axis=1)
    F /= normalization_factor[:, None]

    return F

observations = [int(x) for x in input().split()]
result = forward_algorithm(observations)

for t in range(len(observations)+3):
    if t == 0:
        print(f"Timestep {t}: 0.500")
    else:
        print(f"Timestep {t}: {result[t, 0]:.3f}")