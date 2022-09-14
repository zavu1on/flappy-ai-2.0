import numpy as np
import matplotlib.pyplot as plt


def sigmoid(x, derivative=False):
    """ сигмоида """
    if derivative:
        return sigmoid(x) * (1 - sigmoid(x))
    return 1 / (1 + np.exp(-x))


def show_convergence(epochs, errors):
    plt.plot(epochs, errors)
    plt.show()


# объявляем переменные
X = np.array([
    [0, 1, 0],
    [0, 1, 1],
    [1, 1, 0],
    [1, 1, 1]
])
Y = np.array([0, 0, 1, 1])
weights = 2 * np.random.rand(3) - 1  # от -1 до 1
EPSILON = 0.1
EPOCH_NUM = 10000
epoch_list = []
error_list = []

# тренируем перцептрона
for epoch in range(EPOCH_NUM):
    for i in range(4):
        x = X[i]
        y = Y[i]
        predict_y = sigmoid(np.dot(x, weights))

        err = y - predict_y
        grad = err * sigmoid(predict_y, True)
        delta = np.dot(x, grad)

        weights += delta * EPSILON

        error_list.append(err)
        epoch_list.append(epoch)

# проверяем результат
print(
    sigmoid(np.dot(np.array([1, 0, 0]), weights))
)
print(
    sigmoid(np.dot(np.array([0, 0, 1]), weights))
)

show_convergence(epoch_list, error_list)
