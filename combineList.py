from decimal import Decimal
from collections import deque

# 商品列表
products = [
    {"name": "农夫山泉 380ml/瓶 24瓶/箱 饮用天然水", "price": Decimal("24.12")},
    {"name": "农夫山泉 550ml*24瓶/箱 矿泉水", "price": Decimal("22.83")},
    {"name": "宝矿力 350ml*24盒 电解质运动型饮料", "price": Decimal("51.58")},
    {"name": "农夫山泉 300ml 24瓶/箱 农夫山泉100%NFC橙汁", "price": Decimal("95.05")},
    {"name": "椰树 椰汁味 245ml*24盒 椰子汁", "price": Decimal("64.51")},
    {"name": "农夫山泉 东方树叶 茉莉花茶500ml*15瓶", "price": Decimal("48.06")},
    {"name": "三得利 无糖乌龙茶饮料 0糖0能量0脂 500ml*15瓶", "price": Decimal("44.15")},
    {"name": "维他 250ml*24盒 柠檬茶", "price": Decimal("39.49")},
    {"name": "脉动 600ml/瓶 15瓶/箱 （青柠口味）", "price": Decimal("47.31")},
    {"name": "屈臣氏 330ml*24罐 苏打汽水经典原味黑罐", "price": Decimal("65.26")},
    {"name": "王老吉 310ml/罐 24罐/箱", "price": Decimal("44.97")},
    {"name": "天地壹号 330ml*15罐 果蔬饮料", "price": Decimal("30.02")},
    {"name": "春光 250ml*10盒 0糖椰子汁", "price": Decimal("34.49")},
    {"name": "可口可乐 300ml*24 可乐300ml*24瓶", "price": Decimal("28.76")},
]


class SolutionFinder:
    def __init__(self, min_total=Decimal('495'), max_total=Decimal('500')):
        self.min_total = min_total
        self.max_total = max_total
        self.constraints = {}  # 商品约束字典
        self.found_solutions = set()  # 已找到的解决方案集合

    def set_constraint(self, product_index, min_qty, max_qty):
        """设置单个商品的约束条件"""
        self.constraints[product_index] = {
            "min": min_qty,
            "max": max_qty
        }

    def set_constraints_from_dict(self, constraints_dict):
        """从字典中批量设置约束条件"""
        self.constraints = constraints_dict.copy()

    def initialize_search(self):
        """初始化搜索状态"""
        self.stack = deque()

        # 初始化数量，应用约束的最小值
        initial_quantities = [0] * len(products)
        for idx, constraint in self.constraints.items():
            initial_quantities[idx] = constraint["min"]

        # 计算初始成本
        initial_cost = sum(initial_quantities[i] * products[i]["price"] for i in range(len(products)))

        # 初始状态：(当前索引, 数量数组, 当前成本)
        self.stack.append((0, initial_quantities, initial_cost))

    def find_next_solution(self):
        """寻找下一个满足条件的解决方案"""
        while self.stack:
            idx, quantities, current_cost = self.stack.pop()

            # 如果已处理完所有商品，检查是否满足条件
            if idx == len(products):
                if self.min_total <= current_cost <= self.max_total:
                    # 检查是否满足所有约束
                    valid = True
                    for prod_idx, constraint in self.constraints.items():
                        if not (constraint["min"] <= quantities[prod_idx] <= constraint["max"]):
                            valid = False
                            break

                    if valid:
                        # 检查是否已找到相同的解决方案
                        solution_key = tuple(quantities)
                        if solution_key not in self.found_solutions:
                            self.found_solutions.add(solution_key)
                            return True, quantities, current_cost

                # 当前解决方案不满足条件或已经找到，继续搜索
                continue

            # 如果当前商品已经有约束，使用约束范围
            if idx in self.constraints:
                min_qty = self.constraints[idx]["min"]
                max_qty = self.constraints[idx]["max"]

                # 按照约束范围尝试不同数量
                for qty in range(max_qty, min_qty - 1, -1):
                    new_quantities = quantities[:]
                    new_quantities[idx] = qty
                    new_cost = current_cost + (qty - quantities[idx]) * products[idx]["price"]

                    # 如果成本未超出上限，添加到堆栈
                    if new_cost <= self.max_total:
                        self.stack.append((idx + 1, new_quantities, new_cost))

            else:
                # 获取当前商品价格
                price = products[idx]["price"]

                # 计算最大可能数量（考虑预算上限）
                max_qty = int((self.max_total - current_cost) // price)

                # 尝试不同数量（从大到小尝试，更容易接近目标）
                for qty in range(max_qty, -1, -1):
                    new_quantities = quantities[:]
                    new_quantities[idx] = qty
                    new_cost = current_cost + qty * price

                    # 如果成本未超出上限，添加到堆栈
                    if new_cost <= self.max_total:
                        self.stack.append((idx + 1, new_quantities, new_cost))

        # 没有找到更多的解决方案
        return False, None, None


def setup_constraints():
    """交互式设置商品约束"""
    print("\n===== 设置商品采购约束 =====")
    print("每个商品的约束格式: min,max (如: 0,5 表示数量在0-5之间)")
    print("直接回车则不设置约束，商品数量将在0到最大可能之间自动计算")
    print(", 前留空视作min为0，, 后留空视作max为100")
    print("----------------------------")

    constraints = {}

    for i, product in enumerate(products):
        print(f"{i + 1}. {product['name']} - 单价: {product['price']} 元/箱")
        while True:
            constraint_input = input(f"   设置约束 (min,max): ")

            if constraint_input:
                try:
                    parts = constraint_input.split(',')
                    min_val = int(parts[0]) if parts[0].strip() else 0
                    max_val = int(parts[1]) if len(parts) > 1 and parts[1].strip() else 100
                    constraints[i] = {"min": min_val, "max": max_val}
                    print(f"   已设置: 最少 {min_val} 箱, 最多 {max_val} 箱")
                    break
                except:
                    print("   输入格式错误，请重试")

    return constraints


def setup_default_constraints():
    """设置默认约束（基于原始需求）"""
    # 创建商品名称到索引的映射
    product_to_idx = {p["name"]: i for i, p in enumerate(products)}

    # 指定优先商品及约束条件
    priority_product_0 = "农夫山泉 东方树叶 茉莉花茶500ml*15瓶"
    priority_product_1 = "维他 250ml*24盒 柠檬茶"
    priority_product_2 = "椰树 椰汁味 245ml*24盒 椰子汁"
    priority_product_4 = "农夫山泉 380ml/瓶 24瓶/箱 饮用天然水"
    priority_product_5 = "农夫山泉 550ml*24瓶/箱 矿泉水"

    constraints = {
        product_to_idx[priority_product_0]: {"min": 4, "max": 100},  # 大于等于4
        product_to_idx[priority_product_1]: {"min": 1, "max": 100},  # 大于等于1
        product_to_idx[priority_product_2]: {"min": 1, "max": 100},  # 大于等于1
        product_to_idx[priority_product_4]: {"min": 0, "max": 0},  # 等于0
        product_to_idx[priority_product_5]: {"min": 0, "max": 0},  # 等于0
    }

    return constraints


def set_price_range():
    """设置价格范围"""
    print("\n===== 设置总价范围 =====")

    while True:
        try:
            min_price = Decimal(input("最小总价 (默认495): ") or "495")
            max_price = Decimal(input("最大总价 (默认500): ") or "500")

            if min_price <= max_price:
                return min_price, max_price
            else:
                print("错误: 最小价格必须小于或等于最大价格")
        except:
            print("请输入有效的数字")


def main():
    print("===== 商品组合优化查找程序 =====")

    # 选择约束设置方式
    print("\n请选择约束设置方式:")
    print("1. 使用默认约束（按原始需求）")
    print("2. 手动设置每个商品的约束")
    choice = input("请选择 (1/2): ")

    if choice == "2":
        constraints = setup_constraints()
    else:
        constraints = setup_default_constraints()

    # 设置总价范围
    min_total, max_total = set_price_range()

    # 创建查找器并设置约束
    finder = SolutionFinder(min_total, max_total)
    finder.set_constraints_from_dict(constraints)

    # 初始化搜索
    print("\n开始查找符合条件的商品组合...")
    finder.initialize_search()

    solution_count = 0

    while True:
        success, quantities, total_cost = finder.find_next_solution()

        if not success:
            if solution_count == 0:
                print("未找到满足条件的解决方案。")
            else:
                print("\n已找到所有满足条件的解决方案。")
            break

        solution_count += 1
        print(f"\n第 {solution_count} 个优解:")

        # 显示解决方案详情
        for i, qty in enumerate(quantities):
            if qty > 0:  # 只显示数量大于0的商品
                product = products[i]
                item_cost = qty * product["price"]
                print(f"- {product['name']}: {qty} 箱 x {product['price']} = {item_cost} 元")

        print(f"总成本: {total_cost} 元")

        # 询问用户是否继续
        choice = input("\n是否继续查找更多解决方案？(y/n): ")
        if choice.lower() != 'y':
            break


if __name__ == "__main__":
    main()