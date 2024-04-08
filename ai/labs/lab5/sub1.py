import numpy as np

def forward_algorithm(observations):
    n = len(observations)
    F = np.zeros((n+1, 2))

    # Initialize the probabilities for the first timestep
    F[0, 0] = 0.5
    F[0, 1] = 0.5

    # Transition and observation probabilities
    p_rain_rain = 0.7
    p_rain_no_rain = 0.3
    p_umbrella_rain = 0.9
    p_umbrella_no_rain = 0.2

    for t in range(1, n+1):
        # Compute the probabilities for the current timestep
        F[t, 0] = (F[t-1, 0] * p_rain_rain + F[t-1, 1] * p_rain_no_rain) * p_umbrella_rain if observations[t-1] == 1 else \
                  (F[t-1, 1] * (1-p_rain_rain) + F[t-1, 0] * (1-p_rain_no_rain)) * (1-p_umbrella_rain)
        F[t, 1] = (F[t-1, 0] * p_rain_no_rain + F[t-1, 1] * p_rain_rain) * p_umbrella_no_rain if observations[t-1] == 1 else \
                  (F[t-1, 1] * (1-p_rain_no_rain) + F[t-1, 0] * (1-p_rain_rain)) * (1-p_umbrella_no_rain)

    # Normalize the probabilities
    normalization_factor = np.sum(F, axis=1)
    F /= normalization_factor[:, None]

    return F

# Example usage
observations = [int(x) for x in input().split()]
result = forward_algorithm(observations)

for t in range(len(observations)+1):
    print(f"Timestep {t}: {result[t, 0]:.3f}")