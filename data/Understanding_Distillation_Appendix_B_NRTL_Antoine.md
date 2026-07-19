# Appendix B: NRTL Parameters and Antoine Coefficients

Source: *Understanding Distillation Using Column Profile Maps*, Appendix B, Daniel Beneke, Mark Peters, David Glasser, and Diane Hildebrandt (Wiley, 2013).

## NRTL model

The tables below give the regressed binary interaction parameters for the NRTL model. The source states that the values were obtained from the Dortmund Data Bank through Aspen Plus.

The activity coefficient is calculated as:

$$
\gamma_i = \exp\left[
\frac{\sum_j x_j \tau_{ji}G_{ji}}{\sum_k x_kG_{ki}}
+
\sum_j\frac{x_jG_{ij}}{\sum_kx_kG_{kj}}
\left(
\tau_{ij}-\frac{\sum_mx_m\tau_{mj}G_{mj}}{\sum_kx_kG_{kj}}
\right)
\right]
$$

where

$$
\tau_{ij}=a_{ij}+\frac{b_{ij}}{T\;(\mathrm{K})},
\qquad
G_{ij}=\exp(-c_{ij}\tau_{ij}).
$$

Rows identify component $i$ and columns identify component $j$. Direction matters; for example, for benzene-water, $a_{ij}=45.191$, whereas for water-benzene, $a_{ji}=140.087$.

## Table B.1 - Binary interaction parameter $a_{ij}$

| Component $i$ / Component $j$ | Methanol | Ethanol | Benzene | p-Xylene | Toluene | Chloroform | Water | Acetone |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Methanol | 0.000 | 4.712 | -1.709 | 0.678 | 0.000 | 0.000 | -0.693 | 0.000 |
| Ethanol | -2.313 | 0.000 | 0.569 | 4.075 | 1.146 | 0.000 | -0.801 | -1.079 |
| Benzene | 11.580 | -0.916 | 0.000 | 0.000 | -2.885 | 0.000 | 45.191 | 0.422 |
| p-Xylene | -3.259 | -5.639 | 0.000 | 0.000 | 0.000 | 0 | 2.773 | 0.000 |
| Toluene | 0.000 | -1.722 | 2.191 | 0.000 | 0.000 | 0.000 | -247.879 | -1.285 |
| Chloroform | 0.000 | 0.000 | 0.000 | 0 | 0.000 | 0.000 | -7.352 | 0.538 |
| Water | 2.732 | 3.458 | 140.087 | 162.477 | 627.053 | 8.844 | 0.000 | 0.054 |
| Acetone | 0.000 | -0.347 | -0.102 | 0.000 | 1.203 | 0.965 | 6.398 | 0.000 |

## Table B.2 - Binary interaction parameter $b_{ij}$

Because $b_{ij}/T$ must be dimensionless in the stated NRTL formulation, $b_{ij}$ is expressed in kelvin.

| Component $i$ / Component $j$ | Methanol | Ethanol | Benzene | p-Xylene | Toluene | Chloroform | Water | Acetone |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Methanol | 0.0 | -1162.3 | 892.2 | 295.5 | 371.1 | -71.9 | 173.0 | 114.1 |
| Ethanol | 483.8 | 0.0 | -54.8 | -1202.4 | -113.5 | -148.9 | 246.2 | 479.1 |
| Benzene | -3282.6 | 882.0 | 0.0 | 122.7 | 1124.0 | -375.4 | 591.4 | -239.9 |
| p-Xylene | 1677.6 | 2504.2 | -136.5 | 0.0 | 75.9 | -17.7 | 296.7 | 173.6 |
| Toluene | 446.9 | 992.7 | -863.7 | -91.1 | 0.0 | -57.0 | 14759.8 | 630.1 |
| Chloroform | 690.1 | 690.3 | 313.0 | -120.2 | -25.2 | 0.0 | 3240.7 | -106.4 |
| Water | -617.3 | -586.1 | -5954.3 | -6046.0 | -27269.4 | -1140.1 | 0.0 | 420.0 |
| Acetone | 101.9 | 206.6 | 306.1 | 83.2 | -400.5 | -590.0 | -1809.0 | 0.0 |

## Table B.3 - Binary interaction parameter $c_{ij}$

| Component $i$ / Component $j$ | Methanol | Ethanol | Benzene | p-Xylene | Toluene | Chloroform | Water | Acetone |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Methanol | 0.0 | 0.3 | 0.4 | 0.5 | 0.3 | 0.3 | 0.3 | 0.3 |
| Ethanol | 0.0 | 0.0 | 0.3 | 0.3 | 0.3 | 0.3 | 0.3 | 0.3 |
| Benzene | 0.0 | 0.0 | 0.0 | 0.3 | 0.3 | 0.5 | 0.2 | 0.3 |
| p-Xylene | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.3 | 0.2 | 0.3 |
| Toluene | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 0.2 | 0.3 |
| Chloroform | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 0.3 |
| Water | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 |
| Acetone | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |

> **Symmetry note:** Table B.3 prints only the upper-triangular values. For an unlike pair, the listed $c_{ij}$ is conventionally used symmetrically (that is, $c_{ji}=c_{ij}$), rather than interpreting the printed lower-triangular zeros as directional parameter values.

## Antoine equation

The source gives the vapor-pressure relation as:

$$
\ln(P_i^{\mathrm{VAP}})=A_i-\frac{B_i}{T+C_i}.
$$

## Table B.4 - Antoine equation coefficients

| Coefficient | Methanol | Ethanol | Benzene | p-Xylene | Toluene | Chloroform | Water | Acetone |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| $A$ | 8.07240 | 8.1122 | 6.90565 | 6.99052 | 6.95464 | 6.93710 | 8.01767 | 7.23160 |
| $B$ | 1574.990 | 1592.864 | 1211.033 | 1453.430 | 1344.800 | 1171.200 | 1715.7 | 1277.030 |
| $C$ | 238.870 | 226.184 | 220.790 | 215.307 | 219.482 | 227.000 | 234.268 | 237.230 |

> **Implementation caution:** The equation and coefficient values above are transcribed exactly from the supplied appendix. The numerical scale of these commonly tabulated Antoine constants is typically associated with a base-10 logarithm and specific temperature/pressure units. Verify the intended logarithm base and units against the surrounding book or Aspen source before using them computationally.

## Reference

Beneke, D., Peters, M., Glasser, D., & Hildebrandt, D. (2013). Appendix B: NRTL Parameters and Antoine Coefficients. In *Understanding Distillation Using Column Profile Maps*. John Wiley & Sons. DOI: `10.1002/9781118477304.app2`.
