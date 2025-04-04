import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.cm import viridis
import random
import sys
import numpy as np

def read_rectangles_from_output(file_path, strip_width_dram):
    dram_rectangles = []
    pmem_rectangles = []

    with open(file_path, 'r') as file:
        next(file)  
        for line in file:
            parts = line.split()
            id = parts[0]
            x1 = float(parts[1])
            y1 = float(parts[2])
            x2 = float(parts[3])
            y2 = float(parts[4])
            
            width = abs(x2 - x1)  
            
            rectangle = (id, x1, y1, x2, y2)
            if width > strip_width_dram:
                pmem_rectangles.append(rectangle)
            else:
                dram_rectangles.append(rectangle)

    return dram_rectangles, pmem_rectangles

def normalize_rectangles(rectangles):
    parts_1 = [rect[1] for rect in rectangles]
    parts_2 = [rect[2] for rect in rectangles]
    parts_3 = [rect[3] for rect in rectangles]
    parts_4 = [rect[4] for rect in rectangles]

    avg_1 = sum(parts_1) / len(parts_1)
    avg_2 = sum(parts_2) / len(parts_2)
    avg_3 = sum(parts_3) / len(parts_3)
    avg_4 = sum(parts_4) / len(parts_4)

    normalized_rectangles = [
        (rect[0], round(rect[1] / avg_1, 2), round(rect[2] / avg_2, 2), round(rect[3] / avg_3, 2), round(rect[4] / avg_2, 2))
        for rect in rectangles
    ]

    return normalized_rectangles, avg_1, avg_2, avg_4

def random_placement_algorithm_dram(rectangles, strip_width_dram, m):
    random.shuffle(rectangles)
    levels = []
    current_floor_height = 0 

    for rect in rectangles:
        placed = False
        if levels:
            last_level = levels[-1]
            level_width = sum([r[1] for r in last_level])
            if level_width + rect[1] <= strip_width_dram and len(last_level) < m:
                last_level.append(rect)
                placed = True
        if not placed:
            current_floor_height += max([r[2] for r in levels[-1]]) if levels else 0
            levels.append([rect])

    dram_packing = []
    current_height = 0
    for level in levels:
        level_width = 0
        max_level_height = max([r[2] for r in level]) if level else 0
        for rect in level:
            dram_packing.append((rect[0], level_width, current_height, rect[1], rect[2]))
            level_width += rect[1]
        current_height += max_level_height  

    return dram_packing, current_height

def calculate_dram_packing_height(dram_packing):
    if not dram_packing:
        return 0 
    max_height = 0
    
    for rect in dram_packing:
        rect_end_height = rect[2] + rect[4]  
        max_height = max(max_height, rect_end_height)

    return max_height

def find_all_usable_y_intervals(x_start, x_end, max_height, m, rectangles_placed, step=0.1):
    usable_intervals = []
    current_start = None

    y_range = np.arange(0, max_height + step, step) 

    for y in y_range:
        rounded_y = round(y, 2)
        if can_place_in_level(x_start, x_end, rounded_y, rounded_y + step, m, rectangles_placed):
            if current_start is None:  
                current_start = rounded_y
        else:
            if current_start is not None: 
                usable_intervals.append((current_start, rounded_y))
                current_start = None 

    if current_start is not None:
        usable_intervals.append((current_start, round(max_height, 2)))

    return usable_intervals
        
def can_place_in_level(x_start, x_end, y_start, y_end, m, rectangles_placed, step=0.1):
    """检查在给定的x轴和y轴区间内，是否可以放置新的矩形，而不超过m个重叠的矩形。"""
    y_range = np.arange(y_start, y_end, step)
    y_overlap_ids = {round(float(y), 2): set() for y in y_range}

    for rect_id, rect_x, rect_y, rect_w, rect_h in rectangles_placed:
        rect_x_end = rect_x + rect_w
        rect_y_end = rect_y + rect_h

        if not (rect_y_end <= y_start or rect_y >= y_end) and not (rect_x_end <= x_start or rect_x >= x_end):
            for y in np.arange(max(rect_y, y_start), min(rect_y_end, y_end), step):
                rounded_y = round(float(y), 2)
                if rounded_y not in y_overlap_ids:
                    y_overlap_ids[rounded_y] = set()
                y_overlap_ids[rounded_y].add(rect_id)

    if not y_overlap_ids:
        return True

    max_overlap = max(len(ids) for ids in y_overlap_ids.values())

    if max_overlap >= m:
        return False
    return True

def random_placement_algorithm_pmem(rectangles, temp_dram_packing, strip_width, m, max_height, step=0.1):
    usable_intervals = find_all_usable_y_intervals(0, strip_width, max_height, m, temp_dram_packing, step)
    pmem_packing = []
    if rectangles is None:
        return pmem_packing, 0

    rectangles = sorted(rectangles, key=lambda x: x[4], reverse=True)
    last_y_end = max([interval[1] for interval in usable_intervals], default=0)

    for rect in rectangles:
        placed = False
        for interval in usable_intervals:
            y_start, y_end = interval
            for y in np.arange(y_start, y_end, step):
                rounded_y = round(y, 2)
                if can_place_in_level(0, strip_width, rounded_y, rounded_y + rect[4], m, temp_dram_packing, step):
                    overlapping_rects = [r for r in pmem_packing if not (r[3] + r[1] <= 0 or r[1] >= strip_width) and not (r[2] + r[4] <= rounded_y or r[2] >= rounded_y + rect[4])]
                    current_width = 0 if not overlapping_rects else max(r[1] + r[3] for r in overlapping_rects)
                    pmem_packing.append((rect[0], current_width, rounded_y, rect[1], rect[4]))
                    temp_dram_packing.append((rect[0], current_width, rounded_y, rect[1], rect[4]))
                    placed = True
                    break
            if placed:
                break

        if not placed:
            y = last_y_end
            if can_place_in_level(0, strip_width, y, y + rect[4], m, temp_dram_packing, step):
                overlapping_rects = [r for r in pmem_packing if not (r[3] + r[1] <= 0 or r[1] >= strip_width) and not (r[2] + r[4] <= y or r[2] >= y + rect[4])]
                current_width = 0 if not overlapping_rects else max(r[1] + r[3] for r in overlapping_rects)
                pmem_packing.append((rect[0], current_width, y, rect[1], rect[4]))
                temp_dram_packing.append((rect[0], current_width, y, rect[1], rect[4]))
                last_y_end += rect[4]

    if pmem_packing:
        max_pmem_height = max(y + h for _, _, y, _, h in pmem_packing)
    else:
        max_pmem_height = 0

    return pmem_packing, max_pmem_height





def get_last_element(lst):
    if lst: 
        return lst[-1]
    else:
        return None
    
def plot_rectangles(dram_packing, pmem_packing, strip_width_dram, strip_width_pmem):
    fig, axs = plt.subplots(1, 2, figsize=(24, 6), sharey=True)

    axs[0].set_xlim(0, strip_width_dram)
    axs[1].set_xlim(0, strip_width_pmem)

    highest_y_dram = max(y + h for _, _, y, _, h in dram_packing)
    highest_y_pmem = max(y + h for _, _, y, _, h in pmem_packing)
    highest_y = max(highest_y_dram, highest_y_pmem)
    axs[0].set_ylim(0, highest_y)
    axs[1].set_ylim(0, highest_y)

    axs[0].set_aspect('equal')
    axs[1].set_aspect('equal')

    axs[0].set_title('DRAM Packing Visualization')
    axs[1].set_title('PMEM Visualization')

    for rect_id, x, y, w, h in dram_packing:
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='r', facecolor='none')
        axs[0].add_patch(rect)
        axs[0].text(x + w / 2, y + h / 2, str(rect_id), ha='center', va='center')

    for rect_id, x, y, w, h in pmem_packing:
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='b', facecolor='none')
        axs[1].add_patch(rect)
        axs[1].text(x + w / 2, y + h / 2, str(rect_id), ha='center', va='center')

    plt.show()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        print("Please provide a file name.")
        sys.exit(1)
    strip_width_dram = 4
    strip_width_pmem = 1000                                                        
    m_value = 8
    pmem_rectangles_list=[]
    pmem_rectangles=[]

    rectangles, pmem_rectangles = read_rectangles_from_output(file_path, strip_width_dram)
    rectangles, normalized_width , normalized_heightDRAM, normalized_heightPMEM= normalize_rectangles(rectangles)
    strip_width_dram = strip_width_dram/normalized_width
    strip_width_pmem = strip_width_pmem/normalized_width

    dram_packing, dram_max_ceiling = random_placement_algorithm_dram(rectangles, strip_width_dram, m_value)
    pmem_max_ceiling = 0
    pmem_packing=[]
    while True:
        last_element = get_last_element(dram_packing)
        if not last_element: 
            break

        previous_pmem_packing = pmem_packing.copy()
        previous_max_ceiling = max(dram_max_ceiling, pmem_max_ceiling)

        corresponding_rect = next((rect for rect in rectangles if rect[0] == last_element[0]), None)
        if corresponding_rect:
            pmem_rectangles.append(corresponding_rect)
    
        dram_packing = [rect for rect in dram_packing if rect[0] != last_element[0]]
        dram_max_ceiling=calculate_dram_packing_height(dram_packing)
        temp_dram_packing = dram_packing.copy()
        pmem_packing, pmem_max_ceiling = random_placement_algorithm_pmem(pmem_rectangles, temp_dram_packing, strip_width_pmem, m_value, dram_max_ceiling)
        current_max_ceiling = max(dram_max_ceiling, pmem_max_ceiling)
        if current_max_ceiling > previous_max_ceiling:
            dram_packing.append(last_element)
            pmem_packing = previous_pmem_packing
            break
    print(normalized_heightDRAM*previous_max_ceiling)
