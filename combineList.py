import csv
from collections import deque
from decimal import Decimal


print("===== 商品组合优化查找程序 =====")


def load_products_from_csv(file_path):
    """从CSV文件加载商品信息."""
    products = []
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # 跳过标题行
        for row in reader:
            if len(row) >= 2:
                name = row[0]
                try:
                    price = Decimal(row[1])
                    products.append({"name": name, "price": price})
                except (ValueError, IndexError):
                    print(f"无法处理行: {row}")
    return products


def set_price_range() -> tuple[Decimal, Decimal]:
    """设置价格范围."""
    while True:
        try:
            min_price = Decimal(input("最小总价 (默认495): ") or "495")
            max_price = Decimal(input("最大总价 (默认500): ") or "500")
            if min_price <= max_price:
                return min_price, max_price
            else:
                print("错误: 最小价格必须小于或等于最大价格")
        except Exception:
            print("请输入有效的数字")


def calculate_max_quantity(product_price, max_total):
    """计算商品最大可购买数量."""
    if product_price == Decimal('0'):
        return 100  # 防止除以零
    return int(max_total // product_price)


class SolutionFinder:
    """查找满足条件的商品组合解决方案."""
    
    def __init__(self, min_total=Decimal('495'), max_total=Decimal('500')):
        self.min_total = min_total
        self.max_total = max_total
        self.constraints = {}  # 商品约束字典
        self.found_solutions = set()  # 已找到的解决方案集合
    
    def set_constraint(self, product_index: int, min_qty: int, max_qty: int):
        """设置单个商品的约束条件。
        
        Args:
            product_index (int): 商品索引
            min_qty (int): 最小数量
            max_qty (int): 最大数量
        """
        self.constraints[product_index] = {
            "min": min_qty,
            "max": max_qty
        }
    
    def set_constraints_from_dict(self, constraints_dict: dict):
        """从字典批量设置约束条件."""
        self.constraints = constraints_dict.copy()
    
    def initialize_search(self):
        """初始化搜索状态."""
        self.stack = deque()
        initial_quantities = [0] * len(products)
        for idx, constraint in self.constraints.items():
            initial_quantities[idx] = constraint["min"]
        
        initial_cost = sum(
            initial_quantities[i] * products[i]["price"]
            for i in range(len(products))
        )
        self.stack.append((0, initial_quantities, initial_cost))
    
    def find_next_solution(self):
        """寻找下一个满足条件的解决方案."""
        while self.stack:
            idx, quantities, current_cost = self.stack.pop()
            
            if idx == len(products):
                if self.min_total <= current_cost <= self.max_total:
                    valid = True
                    for prod_idx, constraint in self.constraints.items():
                        if not (constraint["min"] <= quantities[prod_idx] <= constraint["max"]):
                            valid = False
                            break
                    if valid:
                        solution_key = tuple(quantities)
                        if solution_key not in self.found_solutions:
                            self.found_solutions.add(solution_key)
                            return True, quantities, current_cost
                continue
            
            if idx in self.constraints:
                min_val = self.constraints[idx]["min"]
                max_val = self.constraints[idx]["max"]
                for qty in range(max_val, min_val - 1, -1):
                    new_quantities = quantities.copy()
                    new_quantities[idx] = qty
                    new_cost = current_cost + (qty - quantities[idx]) * products[idx]["price"]
                    if new_cost <= self.max_total:
                        self.stack.append((idx + 1, new_quantities, new_cost))
            else:
                price = products[idx]["price"]
                max_possible = (self.max_total - current_cost) // price
                max_qty = int(max_possible)
                for qty in range(max_qty, -1, -1):
                    new_quantities = quantities.copy()
                    new_quantities[idx] = qty
                    new_cost = current_cost + qty * price
                    if new_cost <= self.max_total:
                        self.stack.append((idx + 1, new_quantities, new_cost))
        return False, None, None


def setup_constraints(max_total: Decimal) -> dict:
    """交互式设置商品约束条件，基于最大总价计算默认最大采购数量."""
    constraints = {}
    print("\n===== 设置商品采购约束 =====")
    print("每个商品的约束格式: min,max (如: 0,5 表示数量在0-5之间)")
    print("直接回车则使用自动计算的约束，商品数量将在0到系统计算的最大可能之间")
    print(", 前留空视作min为0，, 后留空视作max为自动计算的最大可能")
    print("----------------------------")
    
    for i, product in enumerate(products):
        # 计算此商品在最大价格下可购买的最大数量
        max_possible = calculate_max_quantity(product["price"], max_total)
        
        print(f"{i + 1}. {product['name']} - 单价: {product['price']} 元/箱")
        print(f"   最大可能数量: {max_possible} 箱")
        
        while True:
            constraint_input = input(f"   设置约束 (min,max): ").strip()
            if not constraint_input:
                # 默认设置: 最小0，最大为计算出的最大可能数量
                constraints[i] = {"min": 0, "max": max_possible}
                print(f"   已设置: 最少 0 箱, 最多 {max_possible} 箱")
                break
            else:
                try:
                    parts = constraint_input.split(',')
                    min_val = int(parts[0]) if parts[0] else 0
                    max_val = int(parts[1]) if len(parts) > 1 and parts[1] else max_possible
                    
                    # 确保min和max不超过最大可选数量
                    if min_val > max_possible:
                        print(f"   警告: 最小值 {min_val} 超过了最大可能数量 {max_possible}，已自动调整为 {max_possible}")
                        min_val = max_possible
                    
                    if max_val > max_possible:
                        print(f"   警告: 最大值 {max_val} 超过了最大可能数量 {max_possible}，已自动调整为 {max_possible}")
                        max_val = max_possible
                    
                    # 确保min不大于max
                    if min_val > max_val:
                        print(f"   警告: 最小值 {min_val} 大于最大值 {max_val}，已自动调整最小值为 {max_val}")
                        min_val = max_val
                    
                    constraints[i] = {"min": min_val, "max": max_val}
                    print(f"   已设置: 最少 {min_val} 箱, 最多 {max_val} 箱")
                    break
                except Exception:
                    print("   输入格式错误，请重试")
    return constraints


def setup_default_constraints(max_total: Decimal) -> dict:
    """设置默认约束（基于原始需求），并计算最大可能数量."""
    product_to_idx = {p["name"]: i for i, p in enumerate(products)}
    constraints = {}
    
    # 先设置基本的最小值约束
    default_min_values = {
        "农夫山泉 东方树叶 茉莉花茶500ml*15瓶": 4,
        "维他 250ml*24盒 柠檬茶": 1,
        "椰树 椰汁味 245ml*24盒 椰子汁": 1,
        "农夫山泉 380ml/瓶 24瓶/箱 饮用天然水": 0,
        "农夫山泉 550ml*24瓶/箱 矿泉水": 0,
    }
    
    # 特殊约束 - 设置为0的产品保持最大值也为0
    zero_max_products = ["农夫山泉 380ml/瓶 24瓶/箱 饮用天然水", "农夫山泉 550ml*24瓶/箱 矿泉水"]
    
    for product_name, idx in product_to_idx.items():
        # 计算最大值
        if product_name in zero_max_products:
            max_val = 0
        else:
            max_val = calculate_max_quantity(products[idx]["price"], max_total)
        
        # 获取默认最小值
        min_val = default_min_values.get(product_name, 0)
        
        # 确保min不超过max
        if min_val > max_val:
            print(f"警告: 商品 '{product_name}' 的最小值 {min_val} 超过了最大可能数量 {max_val}，已自动调整为 {max_val}")
            min_val = max_val
        
        constraints[idx] = {"min": min_val, "max": max_val}
    
    return constraints


def write_solutions_to_csv(solutions, filename='product_solutions.csv', format_type='wide'):
    """将解决方案写入CSV文件.
    
    Args:
        solutions: 解决方案列表，每个元素为 (quantities, total_cost)
        filename: 文件名
        format_type: 格式类型（'wide'或'long'）
    """
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        if format_type == 'wide':
            header = ['方案编号', '总成本']
            header.extend(p["name"] for p in products)
            writer.writerow(header)
            
            for i, (quantities, total_cost) in enumerate(solutions, 1):
                row = [i, total_cost] + quantities
                writer.writerow(row)
        else:
            writer.writerow(['方案编号', '商品名称', '数量', '单价', '小计'])
            
            for i, (quantities, total_cost) in enumerate(solutions, 1):
                for j, qty in enumerate(quantities):
                    if qty > 0:
                        product = products[j]
                        item_cost = qty * product["price"]
                        writer.writerow([i, product["name"], qty, product["price"], item_cost])
                writer.writerow([i, '总计', '', '', total_cost])
                writer.writerow(['', '', '', '', ''])


def main():
    """主程序入口."""
    global products
    
    # 加载商品数据
    products_file = input("商品列表文件（默认为products.csv）：") or "products.csv"
    products = load_products_from_csv(products_file)
    print(f"===== 已找到{len(products)}个商品 =====")
    
    # 首先设置总价范围
    min_total, max_total = set_price_range()
    
    # 选择约束设置方式
    print("\n请选择约束设置方式:")
    print("1. 使用默认约束（按原始需求）")
    print("2. 手动设置每个商品的约束")
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "2":
        constraints = setup_constraints(max_total)
    else:
        constraints = setup_default_constraints(max_total)
    
    # 是否逐个输出
    print("\n是否逐个输出？")
    while True:
        choice = input("请选择 (y/n): ").strip()
        if choice in ["y", "Y", ""]:
            one_by_one = True
            break
        elif choice in ["n", "N"]:
            one_by_one = False
            break
    
    # 初始化查找器
    finder = SolutionFinder(min_total, max_total)
    finder.set_constraints_from_dict(constraints)
    finder.initialize_search()
    
    solution_count = 0
    all_solutions = []
    
    print("\n开始查找符合条件的商品组合...")
    while True:
        success, quantities, total_cost = finder.find_next_solution()
        if not success:
            if solution_count == 0:
                print("未找到满足条件的解决方案。")
            else:
                print(f"\n已找到所有满足条件的解决方案，共 {solution_count} 个。")
            break
        
        solution_count += 1
        print(f"\n第 {solution_count} 个优解:")
        all_solutions.append((quantities, total_cost))
        
        for i, qty in enumerate(quantities):
            if qty > 0:
                product = products[i]
                item_cost = qty * product["price"]
                print(f"- {product['name']}: {qty} 箱 x {product['price']} = {item_cost} 元")
        print(f"总成本: {total_cost} 元")
        
        if not one_by_one:
            continue
        
        choice = input("\n是否继续查找更多解决方案？(y/n): ").strip()
        if choice.lower() != 'y':
            break
    
    # 导出结果
    if solution_count > 0:
        filename = input("\n请输入CSV文件名 (默认: product_solutions.csv): ") or "product_solutions.csv"
        print("\n请选择CSV格式:")
        print("1. 宽格式 - 每行一个解决方案")
        print("2. 长格式 - 每个商品占一行")
        while True:
            choice = input("请选择 (1/2): ").strip()
            if choice in ["1", ""]:
                format_type = 'wide'
                break
            elif choice == "2":
                format_type = 'long'
                break
        
        write_solutions_to_csv(all_solutions, filename, format_type)
        print(f"解决方案已导出到 {filename}")


if __name__ == "__main__":
    main()
