
import tensorflow as tf
'''
   抄袭预测模型，失败产物，本项目未采用
'''
def linear_regression():
    with tf.variable_scope('prepare_data'):
        #1.准备数据
        X = tf.random_normal(shape=[100,1],name='feature')
        y_true = tf.matmul(X,[[0.8]])+0.7
    with tf.variable_scope('create_mode'):
        #构造权重weight 和偏置 使用变量来创建
        weight = tf.Variable(initial_value=tf.random_normal(shape=[1,1]),name='weight')
        bias = tf.Variable(initial_value=tf.random_normal(shape=[1,1]),name='bias')
        y_predict = tf.matmul(X,weight)+bias
    with tf.variable_scope('loss_function'):
        #2.构造损失函数
        error = tf.reduce_mean(tf.square(y_predict-y_true))
    with tf.variable_scope('optimizer'):
        #3.优化损失
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1).minimize(error)
    # （2）增加变量显示 收集变量
    tf.summary.scalar('error',error)
    tf.summary.histogram('weights',weight)
    tf.summary.histogram('bias',bias)
    # （3）增加变量显示 合并变量
    merged = tf.summary.merge_all()

    #（1）保存模型  创建saver对象
    saver = tf.train.Saver()
    #初始化变量
    init = tf.global_variables_initializer()
    with tf.Session() as sess:
        #运行初始化变量
        sess.run(init)
        print('训练前查看模型参数：权重：%f,偏置：%f,损失：%f'%(weight.eval(),bias.eval(),error.eval()))
        # （1）增加变量显示 创建事件文件
        fileWriter = tf.summary.FileWriter('e:/events/test',graph=sess.graph)
        #读取模型
        #判断模型是否存在
        ckpt = tf.train.get_checkpoint_state('./ckpt/')
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess,'./ckpt/linear_regression.ckpt')
        print('训练后模型参数：权重：%f,偏置：%f,损失：%f' % (weight.eval(), bias.eval(), error.eval()))


if __name__ == '__main__':
    linear_regression()