// 示例代码（样例 02 用）：高斯模糊的 pass 安排，只保留和 pass 数有关的几行
void AddBlurPasses(int iterations)
{
    if (iterations <= 0) return; // 不模糊，整个效果跳过
    AddPass("Downsample");
    for (int i = 0; i < iterations; i++)
    {
        AddPass("BlurV");
        AddPass("BlurH");
    }
    AddPass("Upsample");
}
