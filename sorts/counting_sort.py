def counting_sort(nums):
    bucket = [0] * (max(nums) + 1)
    for num in nums:
        bucket[num] += 1
    res = []
    for i in range(len(bucket)):
        res.extend([i] * bucket[i])
    return res