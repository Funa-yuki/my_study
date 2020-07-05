bench_file = open("./benchmark.txt", "r")

# 一行ずつ読み込んでは表示する
bench_sum = float(0)
for line in bench_file:
    bench_sum += float(line)

bench_file.close()

bench_fixed_file = open("./bench_fixed.txt", "r")

# 一行ずつ読み込んでは表示する
bench_fixed_sum = float(0)
for line in bench_fixed_file:
    bench_fixed_sum += float(line)

bench_fixed_file.close()

print("before: {}s".format(bench_sum/100))
print("fixed : {}s".format(bench_fixed_sum/100))
