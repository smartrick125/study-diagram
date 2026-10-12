// 示例代码（样例 02 用）：5 次采样的高斯模糊，只保留和数字有关的几行
float _BlurSpread; // 扩散系数，默认 1.0

static const float weight[3] = {0.4026, 0.2442, 0.0545}; // σ = 1，采样点 0、±1、±2

float4 BlurV(float2 uv, float2 texel)
{
    float4 sum = SampleTex(uv) * weight[0];
    for (int i = 1; i < 3; i++)
    {
        float2 offset = float2(0, texel.y * i * _BlurSpread);
        sum += SampleTex(uv + offset) * weight[i];
        sum += SampleTex(uv - offset) * weight[i];
    }
    return sum;
}
