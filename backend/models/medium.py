from .base import ModelProvider

class MediumModelProvider(ModelProvider):
    name = "Medium LLM"
    tier = "MEDIUM"

    def simulate_response(self, query: str) -> str:
        q = query.lower()
        # Reasoning Benchmark handlers
        if 'bloops' in q or 'razzies' in q:
            return "Yes. By the transitive property of set inclusion, if all bloops are razzies and all razzies are lazzies, all bloops are definitely lazzies."
        elif 'farmer' in q and 'wolf' in q:
            return "The farmer must take the goat across first. Leaving the wolf alone with the cabbage is safe because the wolf does not eat cabbage."
        elif 'copper wire' in q or 'rubber hose' in q:
            return "A copper wire is better suited to conduct electricity because copper has low resistance and free electrons, whereas rubber acts as an insulator."
        elif 'redshift' in q:
            return "The observed redshift indicates that the galaxy is receding and moving away from Earth due to cosmological metric expansion."
        elif 'tuesday' in q and '100 days' in q:
            return "100 divided by 7 equals 14 with a remainder of 2. Advancing 2 days from Tuesday gives Thursday."
        elif 'water expand' in q or 'freezes into ice' in q:
            return "Water expands upon freezing because hydrogen bonding locks molecules into an open hexagonal crystal lattice that occupies greater volume than liquid water."
        elif 'bat and a ball' in q:
            return "The ball costs 5 cents ($0.05). Let ball = x. Then x + (x + 1.00) = 1.10, so 2x = 0.10, which gives x = 0.05 (5 cents)."
        elif 'o(n^2)' in q or 'doubled to 2n' in q:
            return "The runtime increases by a factor of 4. Since runtime scales quadratically with N, (2N)^2 = 4N^2."
        elif 'astronomical seasons' in q or 'causes' in q and 'seasons' in q:
            return "Seasons on Earth are caused by the 23.5-degree axial tilt relative to the orbital plane around the Sun, modulating incident solar energy angles."
        elif '30 people' in q and 'birthday' in q:
            return "The probability is greater than 50%. In a group of 30 people, the birthday paradox calculation yields approximately a 70.6% chance of a shared birthday."

        # Math Benchmark handlers
        elif 'natalia' in q:
            return "In April, Natalia sold 48 clips. In May, she sold 48 / 2 = 24 clips. Altogether: 48 + 24 = 72 clips. The answer is 72."
        elif 'weng' in q and 'babysitting' in q:
            return "Weng earns $12 / 60 = $0.20 per minute. For 50 minutes: 50 * $0.20 = $10. The answer is 10."
        elif 'betty' in q and 'wallet' in q:
            return "Betty has $50. Parents gave $15, grandparents gave 2 * $15 = $30. Total saved: $50 + $15 + $30 = $95. Remaining needed: $100 - $95 = $5. The answer is 5."
        elif 'robe' in q and 'bolts' in q:
            return "Each robe requires 2 + 1 = 3 bolts of fiber. For 150 robes: 150 * 3 = 450 bolts. The answer is 450."
        elif 'josh' in q and 'flipping a house' in q:
            return "Total investment: $80,000 + $50,000 = $130,000. Sale price: $150,000. Profit: $150,000 - $130,000 = $20,000. The answer is 20000."
        elif 'james' in q and 'letter' in q:
            return "James writes 3 pages * 2 friends = 6 pages per session. Writing twice a week gives 6 * 2 = 12 pages per week. The answer is 12."
        elif 'garden' in q and 'flowers' in q:
            return "Total flowers planted: 10 * 5 = 50 flowers. If 15 wilt: 50 - 15 = 35 healthy flowers remain. The answer is 35."
        elif 'f(x) = 3*x^4' in q:
            return "f'(x) = 12*x^3 - 10*x. At x = 2: 12*(8) - 10*(2) = 96 - 20 = 76. The answer is 76."
        elif 'right triangle with base 8' in q:
            return "Using the Pythagorean theorem: height = sqrt(10^2 - 8^2) = sqrt(36) = 6 cm. Area = 0.5 * 8 * 6 = 24 square centimeters. The answer is 24."
        elif '3*x + 15 = 2*(x + 12)' in q:
            return "3*x + 15 = 2*x + 24. Subtracting 2*x from both sides gives x + 15 = 24. Subtracting 15 yields x = 9. The answer is 9."

        # Coding Benchmark handlers
        elif 'has_close_elements' in q:
            return "def has_close_elements(numbers: list, threshold: float) -> bool:\n    for i in range(len(numbers)):\n        for j in range(i + 1, len(numbers)):\n            if abs(numbers[i] - numbers[j]) < threshold:\n                return True\n    return False"
        elif 'separate_paren_groups' in q:
            return "def separate_paren_groups(paren_string: str) -> list:\n    res, cur, depth = [], [], 0\n    for c in paren_string:\n        if c == '(':\n            depth += 1\n            cur.append(c)\n        elif c == ')':\n            depth -= 1\n            cur.append(c)\n            if depth == 0:\n                res.append(''.join(cur))\n                cur = []\n    return res"
        elif 'truncate_number' in q:
            return "def truncate_number(number: float) -> float:\n    return number % 1.0"
        elif 'below_zero' in q:
            return "def below_zero(operations: list) -> bool:\n    bal = 0\n    for op in operations:\n        bal += op\n        if bal < 0:\n            return True\n    return False"
        elif 'mean_absolute_deviation' in q:
            return "def mean_absolute_deviation(numbers: list) -> float:\n    m = sum(numbers) / len(numbers)\n    return sum(abs(x - m) for x in numbers) / len(numbers)"
        elif 'intersperse' in q:
            return "def intersperse(numbers: list, delimiter: int) -> list:\n    if not numbers: return []\n    out = []\n    for n in numbers[:-1]:\n        out.extend([n, delimiter])\n    out.append(numbers[-1])\n    return out"
        elif 'filter_by_substring' in q:
            return "def filter_by_substring(strings: list, substring: str) -> list:\n    return [s for s in strings if substring in s]"
        elif 'sum_squares' in q:
            return "def sum_squares(numbers: list) -> int:\n    return sum(x * x for x in numbers)"
        elif 'is_palindrome' in q:
            return "def is_palindrome(s: str) -> bool:\n    c = [ch.lower() for ch in s if ch.isalnum()]\n    return c == c[::-1]"
        elif 'find_max_subsequence_sum' in q:
            return "def find_max_subsequence_sum(nums: list) -> int:\n    m_so_far = cur = nums[0]\n    for x in nums[1:]:\n        cur = max(x, cur + x)\n        m_so_far = max(m_so_far, cur)\n    return m_so_far"

        # General Knowledge
        elif 'supervised and unsupervised' in q or 'difference between supervised' in q:
            return (
                "Supervised learning trains models on labeled input-output datasets to predict outcomes for new data. "
                "In contrast, unsupervised learning discovers hidden patterns, clusters, or representations in unlabeled data "
                "without human-provided supervision targets."
            )
        elif 'gradient descent' in q and 'fail' in q:
            return (
                "Gradient descent can fail to converge due to several factors: an excessively high learning rate causing divergence, "
                "vanishing or exploding gradients in deep networks, poor initialization trapping the optimizer in saddle points, "
                "or ill-conditioned loss surfaces with high curvature."
            )
        elif 'derivative' in q:
            return (
                "To compute the derivative of the expression, we apply the standard rules of differentiation. "
                "For polynomial terms, the power rule applies: d/dx[x^n] = n*x^(n-1). Adding the derivative of each linear term yields the final analytical result."
            )
        else:
            return (
                "This is a balanced, moderately detailed explanation from the Medium model. "
                "It covers the primary mechanisms, trade-offs, and practical considerations without excessive verbosity."
            )
