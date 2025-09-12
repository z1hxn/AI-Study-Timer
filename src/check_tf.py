import tensorflow as tf, time

def run_test(device):
    with tf.device(device):
        a = tf.random.normal([2000, 2000])
        b = tf.random.normal([2000, 2000])
        start = time.time()
        c = tf.matmul(a, b)
        tf.experimental.numpy.sum(c)  # 강제 연산 실행
        end = time.time()
        print(f"{device} 연산 시간:", end - start, "초")

run_test("/CPU:0")
run_test("/GPU:0")