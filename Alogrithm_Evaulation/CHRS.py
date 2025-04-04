import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
from matplotlib.cm import viridis
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

def calculate_ratio(current_width, strip_width_dram, num_rects_current_level, m):
    numerator = (strip_width_dram - current_width) / strip_width_dram
    denominator = ((m - num_rects_current_level) / m) + ((strip_width_dram - current_width) / strip_width_dram)
    return 0 if denominator == 0 else numerator / denominator

def fill_space_Q(Q_height, Q_width, wide_list, narrow_list, memory_type='DRAM'):

    if memory_type == 'DRAM':
        combined_list = sorted(wide_list + narrow_list, key=lambda x: (-x[1], -x[2]))
    elif memory_type == 'PMEM':
        combined_list = sorted(wide_list + narrow_list, key=lambda x: (-x[1], -x[4]))
    for rect in combined_list:
        rect_id, rect_width, rect_height = rect[:3]
        if rect_width <= Q_width and rect_height <= Q_height:
            return rect  
    return None  

def can_fill_R(x_start, x_end, y_start, y_end, m, strip_width_dram, rectangles_placed):

    y_counts = {}

    step = 0.1

    for rect in rectangles_placed:
        _, rect_x_start, rect_y_start, rect_width, rect_height = rect
        rect_x_end = rect_x_start + rect_width
        rect_y_end = rect_y_start + rect_height

        if not (rect_x_end <= x_start or rect_x_start >= x_end):
            for y in np.arange(max(rect_y_start, y_start), min(rect_y_end, y_end), step):
                rounded_y = round(y, 2)
                y_counts[rounded_y] = y_counts.get(rounded_y, 0) + 1

    for count in y_counts.values():
        if count > m:
            return False  

    return True


def fill_space_R(R_region, wide_list, narrow_list, rectangles_placed, m, memory_type='DRAM', pmem_rectangles_placed=None):
    x_start, x_end, y_start, y_end = R_region['x_start'], R_region['x_end'], R_region['y_start'], R_region['y_end']
    Q_width = x_end - x_start
    Q_height = y_end - y_start

    while Q_height > 0:
        filled_rect = fill_space_Q(Q_height, Q_width, wide_list, narrow_list, memory_type)
        if filled_rect:
            rect_id, rect_width, rect_height = filled_rect[:3]
            x_start_filled = x_start  
            y_start_filled = y_start  
            y_start += rect_height  
            Q_height -= rect_height 

            if memory_type == 'DRAM':
                rectangles_placed.append((rect_id, x_start_filled, y_start_filled, rect_width, rect_height))
            elif memory_type == 'PMEM':
                rectangles_placed.append((rect_id, x_start_filled, y_start_filled, rect_width, rect_height))
                pmem_rectangles_placed.append((rect_id, x_start_filled, y_start_filled, rect_width, rect_height))
            
            if filled_rect in wide_list:
                wide_list.remove(filled_rect)
            else:
                narrow_list.remove(filled_rect)
        else:
            break

def convert_levels_to_packing(rectangles_placed):
    packing_info = []

    for rect in rectangles_placed:
        rect_id, x_start, y_start, rect_width, rect_height = rect
        packing_info.append((rect_id, x_start, y_start, rect_width, rect_height))

    return packing_info


def custom_algorithm_dram(rectangles, strip_width_dram, m):
    wide_list = [rect for rect in rectangles if rect[1] >= rect[2]]
    narrow_list = [rect for rect in rectangles if rect[1] < rect[2]]
    wide_list.sort(key=lambda x: (-x[1], -x[2]))
    narrow_list.sort(key=lambda x: (-x[2], -x[1]))

    levels = []  
    floor_height = 0  
    current_level_width = 0
    ceiling_height = 0  
    m_per_level = {}  
    rectangles_placed = []  
    def find_tallest_in_lists():
        tallest_wide = max(wide_list, key=lambda x: x[2], default=(None, 0, 0))
        tallest_narrow = max(narrow_list, key=lambda x: x[2], default=(None, 0, 0))
        return tallest_wide if tallest_wide[2] >= tallest_narrow[2] else tallest_narrow

    def can_place_in_level(x_start, x_end, y_start, y_end, m, rectangles_placed, step=0.1):
        
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

        max_overlap = max(len(ids) for ids in y_overlap_ids.values())

        if max_overlap >= m:
            return False
        return True


    def can_fit_any_rectangle(current_level_width, strip_width, rectangles, floor_height, ceiling_height, m, rectangles_placed):
        for rect in rectangles:
            rect_width, rect_height = rect[1], rect[2]
            if rect_width <= (strip_width - current_level_width):
                y_start = floor_height
                y_end = y_start + rect_height
                if can_place_in_level(0, strip_width_dram, y_start, y_end, m, rectangles_placed):
                    return True  
        return False  



    while wide_list or narrow_list:
        current_width = sum(rect[3] for rect in rectangles_placed if rect[2] == floor_height)
        can_fit = can_fit_any_rectangle(current_width, strip_width_dram, wide_list + narrow_list, floor_height, ceiling_height, m, rectangles_placed)
        if not levels or not can_fit:
            if levels:  
                floor_height = ceiling_height
                current_width = 0  

            tallest_rect = find_tallest_in_lists()  
            if tallest_rect:
          
                if tallest_rect in wide_list: wide_list.remove(tallest_rect)
                elif tallest_rect in narrow_list: narrow_list.remove(tallest_rect)

                
                x_start = current_width
                y_start = floor_height
                
                current_width += tallest_rect[1]  
                ceiling_height = y_start + tallest_rect[2]  

                
                rectangles_placed.append((tallest_rect[0], x_start, y_start, tallest_rect[1], tallest_rect[2]))

                
                if not levels or levels[-1]: 
                    levels.append([tallest_rect])  
                else:  
                    levels[-1].append(tallest_rect)

        
        current_width = sum(rect[3] for rect in rectangles_placed if rect[2] == floor_height)

        num_rects_current_level = sum(1 for rect in rectangles_placed if rect[2] == floor_height)

        p = calculate_ratio(current_width, strip_width_dram, num_rects_current_level, m)
        can_fit = can_fit_any_rectangle(current_width, strip_width_dram, narrow_list, floor_height, ceiling_height, m, rectangles_placed)
        if p <= 0.5 and can_fit:
            placed = False 
            for i, rect in enumerate(narrow_list):
                y_start = floor_height
                y_end = y_start + rect[2] 
                x_end = current_width + rect[1] 
                
                if y_end <= ceiling_height and can_place_in_level(0, strip_width_dram, y_start, y_end, m, rectangles_placed) and x_end <= strip_width_dram :
                    selected_rect = narrow_list.pop(i)  
                    
                    current_width += selected_rect[1]
                    
                    x_start = current_width - selected_rect[1]
                    
                    rectangles_placed.append((selected_rect[0], x_start, y_start, selected_rect[1], selected_rect[2]))
                    placed = True  
            
                    Q_height = ceiling_height - y_end
                    Q_width = selected_rect[1]
                    attempted_rects = []
                    all_rects = wide_list + narrow_list 
                    while Q_height > 0 and all_rects:
                        rects_to_try = [rect for rect in all_rects if rect not in attempted_rects]
                        if not rects_to_try:  
                            break

                        filled_rect = fill_space_Q(Q_height, Q_width, rects_to_try, [],'DRAM')
                        if filled_rect:
                            rect_id, rect_width, rect_height = filled_rect[:3]
                            x_start_filled = x_start
                            y_start_filled = y_end
                            if not can_place_in_level(0, strip_width_dram, y_start_filled, y_start_filled + rect_height, m, rectangles_placed):
                                attempted_rects.append(filled_rect)
                                continue  
                            y_end += rect_height  
                            Q_height -= rect_height  
                    
                            attempted_rects.append(filled_rect)
                            rectangles_placed.append((rect_id, x_start_filled, y_start_filled, rect_width, rect_height))

                            if filled_rect in wide_list:
                                wide_list.remove(filled_rect)
                            else:
                                narrow_list.remove(filled_rect)
                        else:
                            break
        can_fit = can_fit_any_rectangle(current_width, strip_width_dram, wide_list, floor_height, ceiling_height, m, rectangles_placed)
        if not can_fit:
            placed = False  
            
            for i, rect in enumerate(narrow_list):
                y_start = floor_height
                y_end = y_start + rect[2]  
                x_end = current_width + rect[1] 
                
                if y_end <= ceiling_height and can_place_in_level(0, strip_width_dram, y_start, y_end, m, rectangles_placed) and x_end <= strip_width_dram :
                    selected_rect = narrow_list.pop(i)  
                    
                    current_width += selected_rect[1]
                    
                    x_start = current_width - selected_rect[1]
                    
                    rectangles_placed.append((selected_rect[0], x_start, y_start, selected_rect[1], selected_rect[2]))
                    placed = True  
            
                    
                    Q_height = ceiling_height - y_end
                    Q_width = selected_rect[1]
                    attempted_rects = []
                    all_rects = wide_list + narrow_list 
                    while Q_height > 0 and all_rects:
                        
                        rects_to_try = [rect for rect in all_rects if rect not in attempted_rects]
                        if not rects_to_try:  
                            break

                        filled_rect = fill_space_Q(Q_height, Q_width, rects_to_try, [],'DRAM')
                        if filled_rect:
                            rect_id, rect_width, rect_height = filled_rect[:3]
                            
                            x_start_filled = x_start
                            y_start_filled = y_end
                            if not can_place_in_level(0, strip_width_dram, y_start_filled, y_start_filled + rect_height, m, rectangles_placed):
                                attempted_rects.append(filled_rect)
                                continue  
                            y_end += rect_height  
                            Q_height -= rect_height  
                    
                            
                            attempted_rects.append(filled_rect)
                            rectangles_placed.append((rect_id, x_start_filled, y_start_filled, rect_width, rect_height))

                            
                            if filled_rect in wide_list:
                                wide_list.remove(filled_rect)
                            else:
                                narrow_list.remove(filled_rect)
                        else:
                          
                            break
        else:
            remaining_height = ceiling_height - floor_height
            remaining_width = strip_width_dram - current_width
            wide_rect_found = False  
            wide_used_floor_height = floor_height  
            R_regions = []
            last_x_end = None  

            index = 0
            while index < len(wide_list):
                rect = wide_list[index]
                rect_id, rect_width, rect_height = rect[:3]

                
                y_start = wide_used_floor_height
                y_end = y_start + rect_height
                x_start = current_width  
                x_end = x_start + rect_width  

                if rect_width <= remaining_width and y_end <= ceiling_height and can_place_in_level(0, strip_width_dram, y_start, y_end, m, rectangles_placed):
                    wide_rect_found = True
                    wide_used_floor_height = y_end
                    
        
                    wide_list.pop(index)
    
                    rectangles_placed.append((rect_id, x_start, y_start, rect_width, rect_height))
                    
                    if last_x_end is not None and x_end != last_x_end:
                        R_region = {'x_start': x_end, 'x_end': last_x_end, 'y_start': y_start, 'y_end': ceiling_height}
                        
                        if can_fill_R(x_end, last_x_end, y_start, ceiling_height, m, strip_width_dram, rectangles_placed) and can_place_in_level(0, strip_width_dram, y_start, y_end, m, rectangles_placed):
                            fill_space_R(R_region, wide_list, narrow_list, rectangles_placed, m, 'DRAM')
                    last_x_end = x_end  
                else:
                    index += 1  
        
            
            if wide_rect_found and wide_used_floor_height < ceiling_height:
                
                for narrow_rect in narrow_list:
                    narrow_rect_id, narrow_rect_width, narrow_rect_height = narrow_rect[:3]
                    next_y_start = wide_used_floor_height
                    next_y_end = next_y_start + narrow_rect_height

                    if narrow_rect_width <= remaining_width and next_y_end <= ceiling_height and can_place_in_level(0, strip_width_dram, y_start, y_end, m, rectangles_placed):
                        narrow_list.remove(narrow_rect)  
                        wide_used_floor_height = next_y_end  

                        
                        rectangles_placed.append((narrow_rect_id, x_start, next_y_start, narrow_rect_width, narrow_rect_height))
                        
            if not wide_rect_found:
                if not narrow_list:
                    break
                placed = False  
                
                for i, rect in enumerate(narrow_list):
                    y_start = floor_height
                    y_end = y_start + rect[2]  
                    x_end = current_width + rect[1] 
                    if y_end <= ceiling_height and can_place_in_level(0, strip_width_dram, y_start, y_end, m, rectangles_placed) and x_end <= strip_width_dram :
                        selected_rect = narrow_list.pop(i)  
                        current_width += selected_rect[1]
                        x_start = current_width - selected_rect[1]
                        rectangles_placed.append((selected_rect[0], x_start, y_start, selected_rect[1], selected_rect[2]))
                        placed = True  
            
                        Q_height = ceiling_height - y_end
                        Q_width = selected_rect[1]
                        attempted_rects = []
                        all_rects = wide_list + narrow_list 
                        while Q_height > 0 and all_rects:
                            rects_to_try = [rect for rect in all_rects if rect not in attempted_rects]
                            if not rects_to_try:  
                                break

                            filled_rect = fill_space_Q(Q_height, Q_width, rects_to_try, [], 'DRAM')
                            if filled_rect:
                                rect_id, rect_width, rect_height = filled_rect[:3]
                                x_start_filled = x_start
                                y_start_filled = y_end
                                if not can_place_in_level(0, strip_width_dram, y_start_filled, y_start_filled + rect_height, m, rectangles_placed):
                                    attempted_rects.append(filled_rect)
                                    continue  
                                y_end += rect_height  
                                Q_height -= rect_height  
                    
                                attempted_rects.append(filled_rect)
                                rectangles_placed.append((rect_id, x_start_filled, y_start_filled, rect_width, rect_height))
                                print(f"矩形 {rect_id} 用于填充Q空间，放置于 x={x_start_filled}, y={y_start_filled}, 宽度={rect_width}, 高度={rect_height}")

                                if filled_rect in wide_list:
                                    wide_list.remove(filled_rect)
                                else:
                                    narrow_list.remove(filled_rect)
                            else:
                                break
    dram_packing = convert_levels_to_packing(rectangles_placed)
    return dram_packing, ceiling_height ,rectangles_placed

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


def custom_algorithm_pmem(rectangles, strip_width, m, temp_dram_packing, max_height, step=0.1):
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
            y_range = np.arange(y_start, y_end, step)
            for y in y_range:
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
    
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_rectangles(dram_packing, pmem_packing, strip_width_dram, strip_width_pmem):
    fig, axs = plt.subplots(1, 2, figsize=(15, 6), sharey=False)

    plt.subplots_adjust(wspace=0.1)  

    axs[0].set_xlim(0, strip_width_dram)
    axs[1].set_xlim(0, strip_width_pmem)

    highest_y_dram = max(y + h for _, _, y, _, h in dram_packing)
    highest_y_pmem = max((y + h for _, _, y, _, h in pmem_packing), default=0)
    highest_y = max(highest_y_dram, highest_y_pmem)
    axs[0].set_ylim(0, highest_y)
    axs[1].set_ylim(0, highest_y)

    axs[0].set_aspect('equal')
    axs[1].set_aspect('equal')

    axs[0].set_title('DRAM Packing Visualization')
    axs[1].set_title('PMEM Packing Visualization')

    for rect_id, x, y, w, h in dram_packing:
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='r', facecolor='none')
        axs[0].add_patch(rect)
        axs[0].text(x + w / 2, y + h / 2, str(rect_id), ha='center', va='center')

    if pmem_packing:
        for rect_id, x, y, w, h in pmem_packing:
            rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='b', facecolor='none')
            axs[1].add_patch(rect)
            axs[1].text(x + w / 2, y + h / 2, str(rect_id), ha='center', va='center')
    else:
        axs[1].text(0.5, 0.5, '', ha='center', va='center', fontsize=12, color='grey', transform=axs[1].transAxes)

    plt.show()

def find_min_ratio_rectangle(dram_rectangles):
    min_ratio = float('inf')  
    min_ratio_rect = None  

    for rect in dram_rectangles[1:]:  
        rect_id, dram_width, dram_height, pmem_width, pmem_height = rect
        r = (pmem_height - dram_height) / dram_width  

        if r < min_ratio:  
            min_ratio = r
            min_ratio_rect = rect

    return min_ratio_rect  

def overall_height(dram_max_ceiling, pmem_max_ceiling):
    return max(dram_max_ceiling, pmem_max_ceiling)

def calculate_ratio2(rect):
    return (rect[4] - rect[2]) / rect[1]

def reevaluate_height(dram_rectangles, pmem_rectangles, strip_width_dram, strip_width_pmem, m_value):
    dram_packing, dram_max_ceiling, dram_rectangles_placed = custom_algorithm_dram(dram_rectangles, strip_width_dram, m_value)
    pmem_packing, pmem_max_ceiling = custom_algorithm_pmem(pmem_rectangles, strip_width_pmem, m_value, dram_rectangles_placed, dram_max_ceiling)
    return max(dram_max_ceiling, pmem_max_ceiling), dram_packing, pmem_packing, dram_rectangles_placed
    
if __name__ == "__main__":
    file_path = "random100rectmax16pick50-1.txt"
    strip_width_dram = 32
    strip_width_pmem = 130
    m_value = 8
    pmem_max_ceiling = 0
    pmem_rectangles = []
    dram_rectangles, pmem_rectangles = read_rectangles_from_output(file_path, strip_width_dram)
    dram_rectangles, normalized_width , normalized_heightDRAM, normalized_heightPMEM= normalize_rectangles(dram_rectangles)
    strip_width_dram = strip_width_dram/normalized_width
    strip_width_pmem = strip_width_pmem/normalized_width
    dram_packing, dram_max_ceiling , dram_rectangles_placed = custom_algorithm_dram(dram_rectangles, strip_width_dram, m_value)
    pmem_packing=[]
    current_overall_height = max(dram_max_ceiling, pmem_max_ceiling)
    print(normalized_heightDRAM*current_overall_height)
    min_ratio_rect = find_min_ratio_rectangle(dram_rectangles)
    pmem_rectangles.append(min_ratio_rect)
    dram_rectangles = [rect for rect in dram_rectangles if rect != min_ratio_rect]
    dram_packing, dram_max_ceiling , dram_rectangles_placed = custom_algorithm_dram(dram_rectangles, strip_width_dram, m_value)
    pmem_packing, pmem_max_ceiling  = custom_algorithm_pmem(pmem_rectangles, strip_width_pmem, m_value, dram_rectangles_placed, dram_max_ceiling)
    current_overall_height = max(dram_max_ceiling, pmem_max_ceiling)

    improvement_found = True
    while improvement_found:
        improvement_found = False
        dram_rectangles_sorted_by_ratio = sorted(dram_rectangles, key=lambda rect: calculate_ratio2(rect))
    
        for min_ratio_rect in dram_rectangles_sorted_by_ratio:
            temp_dram_rectangles = [rect for rect in dram_rectangles if rect != min_ratio_rect]
            temp_pmem_rectangles = pmem_rectangles + [min_ratio_rect]

            new_height, temp_dram_packing, temp_pmem_packing, temp_dram_rectangles_placed = reevaluate_height(temp_dram_rectangles, temp_pmem_rectangles, strip_width_dram, strip_width_pmem, m_value)
        
            if new_height < current_overall_height:
                dram_rectangles = temp_dram_rectangles
                pmem_rectangles = temp_pmem_rectangles
                current_overall_height = new_height
                dram_packing = temp_dram_packing
                pmem_packing = temp_pmem_packing
                dram_rectangles_placed = temp_dram_rectangles_placed
                improvement_found = True
                break  
    print(normalized_heightDRAM*current_overall_height)
    plot_rectangles(dram_packing, pmem_packing, strip_width_dram, strip_width_pmem)