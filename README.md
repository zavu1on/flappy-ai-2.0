# Научим птичку летать?

### Для установки выполните
```shell
pip install -r requirements.txt
```

### Для запуска выполните
```shell
python flappy_ai.py
```

### Функции активации
```python
import numpy as np

def sigmoid(x, derivative=False):
    """ сигмоида """
    if derivative:
        return sigmoid(x) * (1 - sigmoid(x))
    return 1 / (1 + np.exp(-x))


def hyperbolic_tangent(x, derivative=False):
    """ гиперболический тангенс """
    if derivative:
        return 1 - hyperbolic_tangent(x) ** 2
    return np.tan(x ** -1)


def single_jump(x, derivative=False):
    """ единичный скачок """
    if derivative:
        return 0
    return int(x >= 0)
```

### Ресурсы
- [Статьи на Хабре про нейросети и обратное распространение](https://habr.com/ru/users/Arnis71/)
- [Нейросеть.Основы](https://www.youtube.com/watch?v=kxXHYCVrnxk&ab_channel=MyGap)
- [Как обучаются нейросети](https://www.youtube.com/watch?v=c89HzsRI0Sg&ab_channel=MyGap)
- [Как работает генетический алгоритм](https://habr.com/ru/post/498914/)
- [Код](https://github.com/zavu1on/flappy-ai-2.0)
- [Notion](https://www.notion.so/zavulon/Flappy-AI-acdc062c83a74f1483fdb777d138a555)
