import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt

def sarsa(env, num_episodes, alpha, gamma, epsilon):
    Q = np.zeros((env.observation_space.n, env.action_space.n))
    episode_returns = []

    for _ in range(num_episodes):
        state, _ = env.reset()
        action = epsilon_greedy_policy(Q, state, epsilon)
        done = False
        episode_return = 0

        while not done:
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            next_action = epsilon_greedy_policy(Q, next_state, epsilon)
            Q[state, action] += alpha * (reward + gamma * Q[next_state, next_action] - Q[state, action])
            state = next_state
            action = next_action
            episode_return += reward

        episode_returns.append(episode_return)

    return episode_returns

def q_learning(env, num_episodes, alpha, gamma, epsilon):
    Q = np.zeros((env.observation_space.n, env.action_space.n))
    episode_returns = []

    for _ in range(num_episodes):
        state, _ = env.reset()
        done = False
        episode_return = 0

        while not done:
            action = epsilon_greedy_policy(Q, state, epsilon)
            next_state, reward, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
            Q[state, action] += alpha * (reward + gamma * np.max(Q[next_state]) - Q[state, action])
            state = next_state
            episode_return += reward

        episode_returns.append(episode_return)

    return episode_returns

def epsilon_greedy_policy(Q, state, epsilon):
    if np.random.uniform(0, 1) < epsilon:
        return env.action_space.sample()
    else:
        return np.argmax(Q[state])

def run_experiment(env, algorithm, num_runs, num_episodes, alpha, gamma, epsilon):
    all_returns = []

    for _ in range(num_runs):
        episode_returns = algorithm(env, num_episodes, alpha, gamma, epsilon)
        all_returns.append(episode_returns)

    avg_returns = np.mean(all_returns, axis=0)
    return avg_returns

if __name__ == "__main__":
    env = gym.make('CliffWalking-v0')
    num_runs = 10
    num_episodes = 1000
    alpha = 0.1
    gamma = 0.99
    epsilon = 0.1

    sarsa_returns = run_experiment(env, sarsa, num_runs, num_episodes, alpha, gamma, epsilon)
    q_learning_returns = run_experiment(env, q_learning, num_runs, num_episodes, alpha, gamma, epsilon)

    plt.figure(figsize=(10, 6))
    plt.plot(sarsa_returns, label='SARSA')
    plt.plot(q_learning_returns, label='Q-Learning')
    plt.xlabel('Episode')
    plt.ylabel('Average Return')
    plt.legend()
    plt.title('SARSA vs Q-Learning on CliffWalking')
    plt.show()