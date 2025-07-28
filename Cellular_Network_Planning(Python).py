import math

from scipy.optimize import brentq
from scipy.special import gammaln

def area_input ():
    """
    Prompt the user for the length and width of a rectangle and return them as a tuple.
    """
    try:
        length = float(input("Enter the length in meters: "))
        width = float(input("Enter the width in meters: "))
        return length*width
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return area_input()  # Retry if input is invalid

def user_density_input():
    """
    Prompt the user for the density of the material and return it.
    """
    try:
        density = float(input("Enter the density in user/km^2: "))
        return density
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
        return user_density_input()  # Retry if input is invalid

def min_carrier_to_interference_ratio_input():
    """
    Prompt the user for the minimum signal-to-noise ratio and return it.
    """
    try:
        min_cir = float(input("Enter the minimum carrier-to-interference ratio: "))
        return min_cir
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
        return min_carrier_to_interference_ratio_input()  # Retry if input is invalid

def erlang_per_user_input():
    """
    Prompt the user for the Erlang per user and return it.
    """
    try:
        erlang_per_user = float(input("Enter the Erlang per user: "))
        return erlang_per_user
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
        return erlang_per_user_input()  # Retry if input is invalid

def trunk_bandwidth_input():
    """
    Prompt the user for the trunk bandwidth and return it.
    """
    try:
        trunk_bandwidth = float(input("Enter the trunk bandwidth in MHz: "))
        return trunk_bandwidth
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
        return trunk_bandwidth_input()  # Retry if input is invalid

def total_bandwidth_input():
    """
    Prompt the user for the total bandwidth and return it.
    """
    try:
        total_bandwidth = float(input("Enter the total bandwidth in MHz: "))
        return total_bandwidth
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
        return total_bandwidth_input()  # Retry if input is invalid

def block_probability_input():
    """
    Prompt the user for the block probability and return it.
    """
    try:
        block_probability = float(input("Enter the block probability: "))
        return block_probability
    except ValueError:
        print("Invalid input. Please enter a numeric value.")
        return block_probability_input()  # Retry if input is invalid


def erlang_b_0(e, m):
    """
    Calculate the Erlang B blocking probability using a more efficient method.
    e: Total traffic intensity in Erlangs
    m: Number of servers (or trunks)
    """
    # Using log-gamma function to avoid overflow for large numbers
    numerator = gammaln(m + 1) - gammaln(m + e + 1)
    denominator = gammaln(e + 1) - gammaln(e + m + 1)

    return math.exp(numerator - denominator)

def erlang_b_1(e, n):
    """
    Calculate the blocking probability using the Erlang B formula.
    e: Total traffic intensity in Erlang
    n: Number of servers (or trunks)
    """
    numerator = (e ** n) / math.factorial(n)
    denominator = sum((e ** k) / math.factorial(k) for k in range(n + 1))
    return numerator / denominator


def erlang_b_2(A, m):
    """
    Calculate Erlang B blocking probability.

    Parameters:
    A (float): offered traffic in Erlangs
    m (int): number of servers/channels

    Returns:
    float: blocking probability
    """
    B = 1.0
    for k in range(1, m + 1):
        B = (A * B) / (k + A * B)
    return B

def inverse_erlang_b(C, B_target):
    """Returns the offered traffic A (in Erlangs) that gives blocking B_target for C trunks."""
    if not (0 < B_target < 1):
        raise ValueError("Blocking probability must be between 0 and 1.")

    def f(A):
        return erlang_b_2(A, C) - B_target

    # Set a safe search interval
    A_min, A_max = 0.001, 500.0

    A_solution = brentq(f, A_min, A_max)
    return float(A_solution)

def main():

    # inputs
    area = area_input() # Area in m^2
    user_density = user_density_input() # User density in user/km^2
    min_c2i = min_carrier_to_interference_ratio_input() # Minimum carrier to interference ratio
    erlang_per_user = erlang_per_user_input()
    trunk_bw = trunk_bandwidth_input() # Trunk bandwidth in MHz
    total_bw = total_bandwidth_input() # Total bandwidth in MHz
    pb = block_probability_input()

    # Displaying inputs
    print("Your inputs are:")
    print(f"Area: {area} m^2 \n")
    area = area / 1000000 # Convert area to km^2
    print(f"User Density: {user_density} user/km^2 \n")
    print(f"Minimum Signal to Noise Ratio: {min_c2i}\n")
    print(f"Erlang per user: {erlang_per_user} \n")
    print(f"Trunk Bandwidth: {trunk_bw} MHz\n")
    print(f"Total Bandwidth of a cell: {total_bw} MHz \n")
    print(f"Block Probability: {pb}")

    # Constants
    N = [3, 4, 7, 9, 12, 13, 16, 19]  # Reuse factors
    # Define sectoring options with their number of sectors
    sectoring_dict = {
        'Omni (360°)': 1,
        '180° sectoring': 2,
        '120° sectoring': 3,
        '60° sectoring': 6
    }

    valid_n_per_N = {}

    for reuse_factor in N:
        valid_sectoring = []
        for name, sectors in sectoring_dict.items():
            n = 6/sectors # Number of interferers
            CIR = (3 * reuse_factor) / n  # Co-channel interference approximation
            if CIR >= min_c2i:
                valid_sectoring.append(name)
        valid_n_per_N[reuse_factor] = valid_sectoring
        #print(f"N = {reuse_factor} --> Valid sectoring options: {valid_sectoring}")

    #cells calculations
    number_of_users = area * user_density
    total_erlang = number_of_users * erlang_per_user

    number_of_trunks_per_cluster = math.floor(total_bw/trunk_bw) #flooring is used to make sure the bandwidth is not exceeded

    best_option = None
    min_cells = float('inf')

    # Calculating the number of cells required for all combinations and the best option
    print("\nReuse Factor and Sectoring Options --> Required Cells:")
    for reuse_factor, sectorings in valid_n_per_N.items():
        for sector in sectorings:
            sectors = sectoring_dict[sector]
            trunks_per_cell = math.floor(number_of_trunks_per_cluster/ (reuse_factor * sectors))
            if trunks_per_cell == 0:
                continue
            #print(f"trunks_per_cell: {trunks_per_cell}")
            erlang_per_sector = inverse_erlang_b(trunks_per_cell, pb)

            # The /sectors is used to get the number of cells
            # Since total_erlang / erlang_per_sector gives the number of sectors, we need to divide by the number of sectors to get the cells
            total_cells = math.ceil(total_erlang / erlang_per_sector / sectors)

            print(f"N = {reuse_factor}, Sectoring = {sector} --> Cells: {total_cells}")

            if total_cells < min_cells:
                min_cells = total_cells
                best_option = (reuse_factor, sector)

    if best_option:
        print(f"\nBest Option → Sectoring = {best_option[1]}, Total Cells = {min_cells}")


#testing_erlang = find_number_of_trunks(0.033, 12)
#print(f"Testing Erlang: {testing_erlang}")

main()


