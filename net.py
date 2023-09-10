from keras.layers import Conv2D, BatchNormalization, Dense, Add, Flatten, Input, Activation
from keras.models import Model


def create_chinese_chess_model():
    num_filters = 256

    # 定义骨干网络
    inputs = Input(shape=(10, 9, 9))
    x = Conv2D(filters=num_filters, kernel_size=3, strides=1, padding='same')(inputs)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)

    # 定义残差网络
    for _ in range(7):
        identity = x

        x = Conv2D(filters=num_filters, kernel_size=3, padding='same')(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)

        x = Conv2D(filters=num_filters, kernel_size=3, padding='same')(x)
        x = BatchNormalization()(x)

        x = Add()([identity, x])
        x = Activation('relu')(x)

    # 策略头
    policy = Conv2D(filters=16, kernel_size=1)(x)
    policy = BatchNormalization()(policy)
    policy = Activation('relu')(policy)
    policy = Flatten()(policy)
    policy = Dense(2086)(policy)

    # 价值头
    value = Conv2D(filters=8, kernel_size=1)(x)
    value = BatchNormalization()(value)
    value = Activation('relu')(value)
    value = Flatten()(value)
    value = Dense(256, activation='relu')(value)
    value = Dense(1, activation='tanh')(value)

    return Model(inputs=inputs, outputs=[policy, value])


if __name__ == '__main__':
    model = create_chinese_chess_model()
    model.summary()