import tensorflow as tf
import numpy as np

'''
   抄袭预测模型，失败产物，本项目未采用
'''
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D#调用matplotlib的3D绘图功能
# 设置学习率
learning_rate = 0.01
# 设置最小误差
threshold = 0.01
# 构造训练数据

# 检测文件的个数
x1_data = np.array([20, 20, 20, 20, 20, 20, 20, 20, 20, 20,
                    30, 30, 30, 30, 30, 30, 30, 30, 30, 30,
                    25, 25, 25, 25, 25, 25, 25, 25, 25, 25])

# 相似度最小值
x2_data = np.array([0.111, 0.211, 0.121, 0.123, 0.323, 0.362, 0.420, 0.423, 0.410, 0.460,
                    0.012, 0.361, 0.243, 0.256, 0.243, 0.125, 0.124, 0.364, 0.620, 0.632,
                    0.812, 0.521, 0.302, 0.180, 0.173, 0.192, 0.112, 0.164, 0.163, 0.339])
# 相似度最大值
x3_data = np.array([0.812, 0.912, 0.916, 0.64, 0.635, 0.754, 0.350, 0.432, 0.762, 0.751,
                    0.360, 0.751, 0.621, 0.663, 0.652, 0.663, 0.761, 0.775, 0.512, 0.954,
                    0.943, 0.998, 0.756, 0.823, 0.854, 0.862, 0.684, 0.635, 0.342, 0.632])
# 总相似度
x4_data = np.array([10.2, 9.32, 8.15, 8.26, 7.11, 6.25, 11.3, 10.6, 10.78, 12.6,
                    14.6, 8.36, 8.43, 8.53, 8.73, 6.35, 6.38, 15.3, 15.9, 17.23,
                    11.23, 14.36, 15.36, 8.23, 7.42, 6.26, 4.36, 14.32, 17.56, 15.71])

y_data = np.array([0.6, 0.73, 0.85, 0.64, 0.57, 0.86, 0.76, 0.94, 0.67, 0.87,
                   0.65, 0.86, 0.63, 0.76, 0.84, 0.67, 0.84, 0.86, 0.76, 0.86,
                   0.76, 0.56, 0.75, 0.86, 0.76, 0.84, 0.76, 0.83, 0.76, 0.73])
# x1_data = np.random.randn(100).astype(np.float32)
# x2_data = np.random.randn(100).astype(np.float32)
#
# y_data = 2 * x1_data + 3 * x2_data + 1
# 构建模型
weight1 = tf.Variable(1.)
weight2 = tf.Variable(1.)
weight3 = tf.Variable(1.)
weight4 = tf.Variable(1.)
bias = tf.Variable(1.)

x1_ = tf.placeholder(tf.float32)
x2_ = tf.placeholder(tf.float32)
x3_ = tf.placeholder(tf.float32)
x4_ = tf.placeholder(tf.float32)

y_ = tf.placeholder(tf.float32)
# 构建模型Y = weight1 * X1 + weight2 * X2 +weight3 * X3 + weight4 * X4 + Bias
y_model = tf.add(
    x=tf.add(
        x=tf.add(x=tf.multiply(weight1, x1_), y=tf.multiply(weight2, x2_)),
        y=tf.add(x=tf.multiply(weight3, x3_), y=tf.multiply(weight4, x4_))
    ),

    y=bias)
# 采用均方差做为损失函数
loss = tf.reduce_mean(tf.pow((y_model - y_), 2))
# 使用随机梯度下降算法
train_op = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss)
with tf.Session() as sess:
    # 参数初始化
    sess.run(tf.global_variables_initializer())
    # 开始训练
    print("Start training!")
    flag = 1
    while (flag):
        # 使用zip进行嵌套，表示三个参数
        for (x, y) in zip(zip(x1_data, x2_data, x3_data, x4_data), y_data):
            sess.run(train_op, feed_dict={x1_: x[0], x2_: x[1], x3_: x[2], x4_: x[3], y_: y})
            # 当训练损失低于threshold时停止训练
            if sess.run(loss, feed_dict={x1_: x[0], x2_: x[1], x3_: x[2], x4_: x[3], y_: y}) < threshold:
                flag = 0
    w1 = sess.run(weight1)
    w2 = sess.run(weight2)
    w3 = sess.run(weight3)
    w4 = sess.run(weight4)
    b = sess.run(bias)
    print('n')
    print('线性回归方程为：')
    print("Y = %f * X1 + %f * X2 + %f * X3 + %f * X4 + %f " % (w1, w2, w3, w4, b))
    # print('n')
    # 绘制模型图
    # fig = plt.figure()
    # ax = Axes3D(fig)
    # X, Y = np.meshgrid(x1_data, x2_data)
    # Z = sess.run(weight1) * (X) + sess.run(weight2) * (Y) + sess.run(bias)
    # ax.plot_surface(X, Y, Z, rstride = 1, cstride = 1, cmap = plt.cm.hot)
    # ax.contourf(X, Y, Z, zdir = 'z', offset = -1, camp = plt.cm.hot)
    # ax.set_title('analysis')
    # ax.set_ylabel('salary')
    # ax.set_xlabel('age')
    # ax.set_zlabel('amount')
    # ax.set_zlim(-1, 1)
    # plt.show()
