import pandas as pd
from pygnuplot import gnuplot

# 讀取 Excel 文件
df = pd.read_excel('fig3.xlsx')

# 從 excel 中提取數據
task = df['Core Amount'].tolist()   #對應excel的Core Amount
FFDH_FF = df['FFDH_FF'].tolist()    #對應excel的FFDH_FF
BFDH_FF = df['BFDH_FF'].tolist()    #對應excel的BFDH_FF
FPAMR = df['FPAMR'].tolist()        #對應excel的FPAMR
Random_FF = df['Random_FF'].tolist()#對應excel的Random_FF
Wontgoback_Random_FF = df['Wontgoback_Random_FF'].tolist()#對應excel的Wontgoback_Random_FF

# 找出 y 軸數據的最大值和最小值
y_min = min(min(FFDH_FF), min(BFDH_FF), min(FPAMR), min(Random_FF), min(Wontgoback_Random_FF))
y_max = max(max(FFDH_FF), max(BFDH_FF), max(FPAMR), max(Random_FF), max(Wontgoback_Random_FF))

# 初始化 gnuplot
g = gnuplot.Gnuplot()
g('set terminal png size 800,600 font "Arial,16"')  # 設定輸出格式和大小
g('set output "fig3.png"')         # 設定輸出文件名
#g('set title "Comparisons of Algorithms Across Different Core Amounts" font "Arial,16"')  # 設定圖表標題
g('set xlabel "Number of Cores" font "Arial,18"')       # 設定 x 軸標籤
g('set ylabel "Completion Time (seconds)" font "Arial,18"')  # 設定 y 軸標籤
g('set grid')                      # 啟用網格
g('set key right top box lw 1')
# 設定 x 軸範圍，使數據不緊貼邊框
x_min = min(task) - (max(task) - min(task)) * 0.05  # 左邊留 5% 的邊距
x_max = max(task) + (max(task) - min(task)) * 0.05  # 右邊留 5% 的邊距
g(f'set xrange [{x_min}:{x_max}]')

# 設定 y 軸範圍，使數據不緊貼邊框
y_margin = (y_max - y_min) * 0.1  # 額外留 10% 的邊距
g(f'set yrange [{y_min - y_margin}:{y_max + y_margin}]')

# 準備繪圖命令，包含數據，並指定不同的點類型
plot_command = '''
plot '-' with linespoints pointtype 7 pointsize 1 title 'CHRS', \
     '-' with linespoints pointtype 5 pointsize 1 title 'FFDH', \
     '-' with linespoints pointtype 9 pointsize 1 title 'BFDH', \
     '-' with linespoints pointtype 11 pointsize 1 title 'Fixed-Level Random', \
     '-' with linespoints pointtype 13 pointsize 1 title 'Flexible-Level Random'
'''
g(plot_command)

# 插入每個數據系列
for data in [FPAMR, FFDH_FF, BFDH_FF, Random_FF, Wontgoback_Random_FF]:
    for x, y in zip(task, data):
        g(f'{x} {y}')
    g('e')  # 結束一個數據集

g('set output')  # 關閉輸出文件
g('exit')  # 退出 gnuplot
