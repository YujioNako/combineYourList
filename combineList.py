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


products_file = input("商品列表文件（默认为products.csv）：") or "products.csv"
products = load_products_from_csv(products_file)
print(f"===== 已找到{len(products)}个商品 =====")


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


def setup_constraints() -> dict:
    """交互式设置商品约束条件."""
    constraints = {}
    print("\n===== 设置商品采购约束 =====")
    print("每个商品的约束格式: min,max (如: 0,5 表示数量在0-5之间)")
    print("直接回车则不设置约束，商品数量将在0到最大可能之间自动计算")
    print(", 前留空视作min为0，, 后留空视作max为100")
    print("----------------------------")
    
    for i, product in enumerate(products):
        print(f"{i + 1}. {product['name']} - 单价: {product['price']} 元/箱")
        while True:
            constraint_input = input(f"   设置约束 (min,max): ").strip()
            if constraint_input:
                try:
                    parts = constraint_input.split(',')
                    min_val = int(parts[0]) if parts[0] else 0
                    max_val = int(parts[1]) if len(parts) > 1 and parts[1] else 100
                    constraints[i] = {"min": min_val, "max": max_val}
                    print(f"   已设置: 最少 {min_val} 箱, 最多 {max_val} 箱")
                    break
                except Exception:
                    print("   输入格式错误，请重试")
    return constraints


def setup_default_constraints() -> dict:
    """设置默认约束（基于原始需求）."""
    product_to_idx = {p["name"]: i for i, p in enumerate(products)}
    constraints = {
        product_to_idx["农夫山泉 东方树叶 茉莉花茶500ml*15瓶"]: {"min": 4, "max": 100},
        product_to_idx["维他 250ml*24盒 柠檬茶"]: {"min": 1, "max": 100},
        product_to_idx["椰树 椰汁味 245ml*24盒 椰子汁"]: {"min": 1, "max": 100},
        product_to_idx["农夫山泉 380ml/瓶 24瓶/箱 饮用天然水"]: {"min": 0, "max": 0},
        product_to_idx["农夫山泉 550ml*24瓶/箱 矿泉水"]: {"min": 0, "max": 0},
    }
    return constraints


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
    # 选择约束设置方式
    print("\n请选择约束设置方式:")
    print("1. 使用默认约束（按原始需求）")
    print("2. 手动设置每个商品的约束")
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "2":
        constraints = setup_constraints()
    else:
        constraints = setup_default_constraints()
    
    # 设置总价范围
    min_total, max_total = set_price_range()
    
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
