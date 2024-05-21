import torch
#from hitsgnn import HITSGNN
from hitsgnn_rev2 import HITSGNN
from utils import *
import argparse
import numpy as np
from metattack import MetaApprox, Metattack
import torch.nn.functional as F
import torch.optim as optim
import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int, default=19, help='Random seed.')
parser.add_argument('--epochs', type=int, default=200,
                    help='Number of epochs to train.')
parser.add_argument('--lr', type=float, default=0.01,
                    help='Initial learning rate.')
parser.add_argument('--hidden', type=int, default=16,
                    help='Number of hidden units.')
parser.add_argument('--dataset', type=str, default='cora',
                    choices=['cora', 'cora_ml', 'citeseer', 'polblogs'], help='dataset')
parser.add_argument('--ptb_rate', type=float, default=0.09,  help='pertubation rate')
parser.add_argument('--model', type=str, default='Meta-Self', choices=['A-Meta-Self', 'Meta-Self'], help='model variant')

args = parser.parse_args()
cuda = torch.cuda.is_available()
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

np.random.seed(args.seed)
torch.manual_seed(args.seed)
if device != 'cpu':
    torch.cuda.manual_seed(args.seed)

# === loading dataset
adj, features, labels = load_data(dataset=args.dataset)
nclass = max(labels) + 1

val_size = 0.1
test_size = 0.8
train_size = 1 - test_size - val_size

idx = np.arange(adj.shape[0])
idx_train, idx_val, idx_test = get_train_val_test(idx, train_size, val_size, test_size, stratify=labels)


print("idx_test", type(idx_test))


idx_test1=[0, 2050, 4, 2057, 11, 2059, 2060, 16, 2065, 21, 36, 38, 39, 40, 41, 2090, 43, 45, 49, 53, 2104, 56, 2110, 2112, 69, 2116, 2124, 2128, 2129, 2131, 80, 85, 86, 87, 2137, 2138, 91, 2140, 2143, 95, 2147, 99, 102, 103, 2157, 2159, 2161, 2162, 114, 2164, 118, 2167, 2168, 2169, 2166, 123, 125, 126, 2177, 128, 132, 139, 2187, 141, 2189, 143, 145, 2194, 2191, 2197, 151, 2199, 2201, 2198, 154, 2205, 2209, 2211, 164, 2218, 2219, 171, 173, 2220, 2223, 177, 2226, 2228, 2229, 184, 187, 188, 189, 2241, 2242, 196, 2244, 197, 200, 202, 2250, 203, 210, 2260, 214, 2263, 216, 215, 225, 226, 2275, 229, 2278, 230, 232, 233, 235, 2286, 240, 2290, 2291, 243, 245, 244, 2294, 253, 254, 256, 2306, 2307, 2308, 260, 258, 262, 264, 266, 267, 268, 269, 271, 273, 274, 275, 2325, 281, 2332, 2333, 284, 287, 288, 2338, 2339, 296, 297, 299, 2351, 303, 304, 308, 310, 311, 312, 313, 314, 2361, 2362, 2364, 316, 2369, 324, 326, 2376, 331, 2380, 334, 337, 339, 341, 343, 347, 348, 355, 2406, 362, 2411, 2413, 369, 370, 371, 2420, 2427, 2429, 385, 388, 2437, 390, 393, 2441, 395, 2444, 397, 398, 399, 2448, 2445, 2449, 403, 406, 407, 412, 2462, 415, 414, 418, 423, 424, 2472, 426, 2475, 429, 2478, 430, 433, 2483, 2484, 442, 445, 447, 449, 456, 461, 464, 473, 474, 476, 477, 479, 481, 484, 487, 498, 509, 511, 513, 517, 520, 525, 528, 530, 531, 533, 534, 537, 538, 542, 544, 546, 557, 566, 585, 588, 590, 595, 600, 602, 603, 607, 609, 610, 613, 614, 615, 626, 644, 647, 648, 652, 658, 659, 661, 665, 666, 669, 670, 672, 673, 674, 679, 684, 689, 691, 696, 698, 701, 702, 705, 707, 711, 715, 717, 718, 719, 720, 724, 727, 729, 735, 147, 748, 756, 764, 766, 768, 777, 778, 779, 788, 2192, 794, 795, 797, 805, 816, 828, 829, 830, 834, 835, 836, 840, 841, 842, 844, 847, 852, 856, 857, 859, 860, 862, 866, 868, 872, 879, 883, 887, 896, 900, 911, 912, 915, 916, 938, 939, 946, 947, 948, 951, 958, 968, 973, 977, 981, 992, 993, 996, 999, 1001, 1002, 1004, 1015, 1016, 1018, 1019, 1029, 1034, 1039, 1048, 1051, 1060, 1061, 1064, 1071, 1085, 1091, 1092, 1100, 1101, 1119, 1120, 1122, 1131, 1134, 1145, 1147, 1148, 1149, 1158, 1163, 1168, 1174, 1176, 1187, 1188, 1201, 1219, 1224, 1225, 1226, 1228, 1229, 1235, 1239, 1240, 1243, 1245, 1246, 1256, 1260, 1262, 1263, 1264, 1266, 1269, 1274, 1278, 1282, 1283, 1284, 1292, 1301, 1305, 1314, 1319, 1330, 1340, 1353, 1361, 1372, 1376, 1384, 1385, 1388, 1397, 1405, 1407, 1409, 1415, 1435, 1438, 1440, 1441, 1442, 1446, 1447, 1461, 1468, 1478, 1479, 1494, 1499, 1505, 1506, 1511, 1516, 1518, 1525, 1537, 1541, 1543, 1544, 1546, 1550, 1555, 1562, 1566, 1573, 1575, 1576, 1585, 1587, 1588, 1596, 1602, 1604, 1605, 1608, 1609, 1614, 1616, 1617, 1618, 1619, 1620, 1621, 1624, 1626, 1631, 1634, 1636, 1642, 1651, 1662, 1670, 1675, 1679, 1681, 1685, 1690, 1692, 1693, 1694, 1695, 1702, 1705, 1706, 1708, 1709, 1710, 1719, 1720, 1725, 1727, 1740, 1746, 1749, 1750, 1758, 1759, 1762, 1763, 1767, 1769, 1780, 1808, 1823, 1830, 1833, 1834, 1835, 1837, 1844, 1845, 1846, 1847, 1856, 1862, 1865, 1866, 1878, 1880, 1882, 1891, 1892, 1893, 1894, 1895, 1897, 1899, 1907, 1911, 1918, 1919, 1920, 1922, 1926, 1931, 1940, 1944, 1961, 1966, 1981, 1982, 1988, 1992, 1993, 1995, 1998, 1999, 2000, 2001, 2003, 2004, 2008, 2009, 2012, 2013, 2016, 2017, 2024, 2027, 2032, 2033, 2037]

idx_test2=[2048, 11, 12, 13, 2061, 15, 16, 2066, 20, 2068, 2069, 21, 22, 29, 31, 32, 34, 2080, 2082, 2083, 38, 36, 2086, 42, 43, 44, 45, 2099, 54, 56, 2105, 58, 2108, 2110, 65, 2122, 2131, 2140, 2143, 2147, 2150, 2153, 2154, 2162, 2163, 2164, 2166, 2167, 2168, 2170, 2173, 2174, 2176, 2177, 2179, 2184, 2186, 2191, 2196, 2206, 2208, 2209, 2211, 2214, 2218, 2228, 2232, 2235, 2236, 2238, 2243, 2256, 2259, 2260, 2262, 2264, 2273, 2274, 2275, 2286, 2290, 2291, 2295, 2296, 2299, 2300, 2301, 2303, 2304, 2306, 2311, 2312, 2313, 2321, 2322, 2326, 2332, 2341, 2343, 2344, 2345, 2347, 2351, 2352, 2360, 2361, 2362, 2371, 2374, 2381, 2385, 2387, 2391, 2392, 2393, 2394, 2398, 2402, 2405, 2406, 2413, 2421, 2427, 2431, 391, 2445, 2446, 2447, 2448, 2453, 2455, 2456, 2461, 2467, 2484, 638, 683, 812, 819, 820, 823, 825, 826, 833, 835, 836, 838, 839, 840, 842, 844, 846, 847, 849, 851, 852, 856, 857, 860, 861, 862, 863, 866, 868, 869, 871, 872, 876, 877, 892, 901, 904, 905, 909, 911, 912, 914, 925, 926, 928, 930, 933, 936, 938, 943, 948, 952, 954, 969, 979, 980, 982, 984, 990, 994, 1001, 1002, 1006, 1007, 1013, 1015, 1019, 1021, 1023, 1024, 1025, 1032, 1035, 1039, 1042, 1046, 1061, 1062, 1064, 1066, 1071, 1073, 1078, 1079, 1085, 1088, 1089, 1097, 1100, 1101, 1104, 1105, 1110, 1111, 1120, 1121, 1127, 1132, 1133, 1138, 1140, 1141, 1145, 1149, 1150, 1158, 1159, 1160, 1163, 1170, 1176, 1179, 1184, 1187, 1189, 1205, 1229, 1233, 1234, 1236, 1238, 1241, 1242, 1244, 1247, 1255, 1256, 1257, 1258, 1260, 1263, 1264, 1265, 1271, 1280, 1281, 1283, 1288, 1289, 1295, 1299, 1300, 1304, 1305, 1309, 1310, 1311, 1313, 1323, 1324, 1325, 1331, 1336, 1338, 1339, 1340, 1345, 1347, 1348, 1350, 1353, 1358, 1366, 1367, 1372, 1376, 1377, 1381, 1382, 1386, 1388, 1389, 1397, 1398, 1399, 1403, 1411, 1412, 1413, 1430, 1436, 1440, 1443, 1454, 1457, 1460, 1465, 1476, 1478, 1479, 1484, 1489, 1493, 1494, 1495, 1497, 1499, 1501, 1505, 1507, 1508, 1509, 1510, 1513, 1514, 1516, 1523, 1524, 1526, 1529, 1531, 1532, 1534, 1535, 1536, 1546, 1549, 1553, 1558, 1560, 1566, 1572, 1576, 1578, 1581, 1586, 1589, 1592, 1601, 1604, 1606, 1608, 1610, 1621, 1622, 1623, 1624, 1626, 1634, 1639, 1642, 1648, 1651, 1654, 1664, 1669, 1670, 1678, 1679, 1684, 1686, 1688, 1689, 1693, 1694, 1711, 1716, 1723, 1726, 1727, 1732, 1733, 1746, 1750, 1752, 1756, 1758, 1761, 1763, 1767, 1772, 1773, 1775, 1778, 1780, 1781, 1802, 1804, 1805, 1806, 1811, 1820, 1821, 1822, 1825, 1833, 1835, 1836, 1837, 1838, 1839, 1840, 1845, 1847, 1853, 1854, 1856, 1858, 1865, 1868, 1874, 1890, 1892, 1893, 1894, 1895, 1896, 1901, 1903, 1907, 1909, 1910, 1920, 1930, 1934, 1939, 1956, 1972, 1973, 1974, 1990, 1992, 1993, 2001, 2003, 2004, 2005, 2007, 2008, 2010, 2027, 2032, 2034, 2038, 2046]

idx_test3=[0, 4, 6, 8, 10, 11, 16, 22, 23, 25, 26, 29, 31, 35, 36, 38, 39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51, 53, 54, 56, 58, 63, 65, 69, 70, 72, 73, 74, 76, 77, 78, 80, 85, 86, 87, 89, 91, 92, 94, 95, 97, 99, 100, 102, 103, 108, 112, 113, 114, 115, 116, 117, 118, 120, 121, 122, 125, 126, 127, 131, 132, 133, 134, 135, 136, 138, 139, 141, 142, 143, 145, 147, 148, 149, 151, 152, 153, 154, 158, 161, 162, 163, 164, 166, 168, 169, 170, 171, 173, 175, 177, 180, 181, 182, 183, 184, 185, 187, 188, 189, 191, 192, 195, 196, 199, 200, 202, 203, 205, 209, 212, 213, 214, 215, 217, 218, 220, 221, 223, 225, 227, 228, 229, 230, 232, 235, 236, 238, 239, 240, 243, 244, 246, 248, 250, 252, 253, 254, 255, 256, 257, 258, 259, 261, 262, 263, 266, 267, 268, 269, 270, 271, 272, 273, 275, 276, 278, 279, 284, 286, 287, 288, 293, 297, 299, 301, 302, 304, 309, 310, 312, 313, 314, 316, 317, 321, 322, 326, 328, 329, 330, 331, 334, 335, 337, 340, 342, 343, 344, 346, 347, 349, 353, 354, 355, 357, 362, 363, 365, 366, 367, 369, 370, 371, 376, 377, 379, 380, 382, 383, 385, 388, 389, 390, 392, 393, 394, 395, 398, 399, 401, 404, 406, 407, 411, 412, 415, 416, 418, 419, 420, 422, 423, 424, 426, 427, 429, 432, 433, 434, 436, 441, 443, 444, 445, 446, 447, 449, 450, 451, 454, 455, 461, 464, 467, 469, 472, 473, 474, 476, 477, 478, 479, 480, 482, 484, 485, 486, 487, 490, 491, 493, 495, 498, 501, 503, 504, 505, 507, 508, 509, 510, 511, 512, 513, 517, 518, 520, 523, 527, 528, 529, 531, 533, 534, 536, 537, 538, 540, 541, 542, 546, 547, 548, 549, 552, 555, 557, 559, 566, 568, 569, 572, 573, 577, 579, 581, 582, 584, 587, 588, 589, 590, 593, 595, 597, 599, 600, 603, 604, 605, 607, 609, 610, 611, 613, 614, 615, 617, 618, 620, 621, 622, 625, 626, 629, 631, 632, 633, 636, 637, 643, 647, 648, 651, 652, 654, 657, 658, 660, 661, 665, 666, 667, 668, 669, 672, 673, 674, 675, 678, 682, 684, 687, 689, 690, 691, 693, 694, 696, 698, 699, 701, 702, 703, 704, 706, 707, 708, 710, 711, 712, 715, 717, 718, 720, 721, 722, 724, 726, 727, 729, 735, 737, 738, 739, 740, 742, 744, 747, 748, 749, 751, 753, 754, 755, 756, 757, 758, 760, 766, 768, 769, 771, 772, 773, 774, 775, 777, 779, 780, 781, 782, 787, 788, 791, 792, 795, 796, 797, 804, 805, 806, 809, 811, 813, 814, 823, 828, 829, 830, 831, 834, 835, 836, 838, 840, 841, 842, 844, 845, 847, 849, 856, 857, 859, 860, 862, 863, 866, 868, 869, 876, 877, 879, 881, 883, 884, 885, 887, 888, 890, 891, 892, 894, 896, 898, 900, 907, 909, 914, 916, 919, 924, 926, 930, 932, 934, 935, 938, 939, 944, 945, 946, 947, 948, 949, 950, 951, 963, 964, 965, 966, 968, 969, 972, 973, 975, 976, 979, 980, 981, 986, 987, 990, 993, 994, 995, 996, 997, 999, 1000, 1002, 1004, 1007, 1009, 1011, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1022, 1025, 1029, 1032, 1034, 1038, 1040, 1048, 1049, 1051, 1053, 1055, 1057, 1059, 1060, 1061, 1064, 1067, 1068, 1069, 1071, 1078, 1085, 1087, 1092, 1093, 1094, 1099, 1100, 1104, 1106, 1119, 1120, 1122, 1123, 1124, 1129, 1130, 1132, 1133, 1134, 1136, 1139, 1142, 1143, 1145, 1149, 1153, 1155, 1156, 1158, 1160, 1161, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1172, 1174, 1184, 1187, 1188, 1191, 1194, 1195, 1197, 1199, 1201, 1206, 1209, 1213, 1214, 1217, 1223, 1226, 1228, 1229, 1233, 1234, 1235, 1238, 1239, 1240, 1243, 1244, 1251, 1256, 1257, 1260, 1262, 1263, 1264, 1265, 1268, 1269, 1271, 1272, 1274, 1277, 1282, 1283, 1284, 1295, 1298, 1301, 1303, 1304, 1305, 1309, 1314, 1319, 1320, 1321, 1322, 1330, 1333, 1334, 1337, 1340, 1345, 1347, 1348, 1353, 1356, 1361, 1362, 1363, 1366, 1367, 1370, 1372, 1376, 1382, 1384, 1385, 1388, 1389, 1395, 1399, 1404, 1405, 1406, 1407, 1409, 1417, 1421, 1423, 1424, 1425, 1427, 1428, 1431, 1432, 1433, 1434, 1435, 1438, 1440, 1441, 1444, 1446, 1447, 1450, 1455, 1457, 1459, 1460, 1461, 1463, 1465, 1466, 1468, 1478, 1479, 1481, 1486, 1489, 1490, 1491, 1493, 1494, 1499, 1505, 1506, 1508, 1511, 1516, 1518, 1519, 1520, 1527, 1528, 1529, 1530, 1535, 1536, 1537, 1540, 1544, 1546, 1550, 1556, 1558, 1559, 1562, 1563, 1564, 1566, 1573, 1575, 1576, 1582, 1585, 1587, 1596, 1601, 1602, 1604, 1605, 1608, 1609, 1610, 1611, 1613, 1614, 1616, 1617, 1618, 1619, 1620, 1621, 1623, 1624, 1625, 1626, 1628, 1629, 1631, 1633, 1634, 1635, 1636, 1639, 1641, 1642, 1646, 1648, 1651, 1655, 1656, 1657, 1658, 1661, 1662, 1663, 1666, 1670, 1676, 1678, 1679, 1681, 1682, 1683, 1685, 1688, 1690, 1691, 1692, 1693, 1694, 1695, 1697, 1701, 1702, 1705, 1706, 1708, 1709, 1710, 1713, 1718, 1719, 1720, 1721, 1725, 1727, 1729, 1740, 1741, 1746, 1750, 1752, 1754, 1756, 1758, 1759, 1760, 1761, 1762, 1763, 1765, 1767, 1769, 1771, 1773, 1774, 1778, 1780, 1784, 1786, 1787, 1793, 1795, 1796, 1798, 1805, 1806, 1808, 1809, 1812, 1814, 1815, 1816, 1818, 1820, 1822, 1823, 1826, 1830, 1834, 1835, 1837, 1838, 1839, 1840, 1841, 1842, 1844, 1846, 1847, 1855, 1856, 1859, 1860, 1861, 1863, 1865, 1867, 1871, 1872, 1873, 1874, 1875, 1877, 1878, 1879, 1882, 1884, 1886, 1889, 1890, 1891, 1892, 1893, 1894, 1895, 1897, 1898, 1899, 1902, 1907, 1909, 1910, 1911, 1918, 1919, 1920, 1922, 1924, 1926, 1927, 1928, 1929, 1930, 1931, 1936, 1938, 1940, 1944, 1945, 1947, 1948, 1949, 1950, 1953, 1954, 1955, 1956, 1960, 1961, 1964, 1965, 1966, 1974, 1979, 1981, 1982, 1984, 1986, 1987, 1988, 1990, 1992, 1993, 1996, 1999, 2000, 2002, 2003, 2004, 2007, 2008, 2009, 2012, 2013, 2017, 2021, 2024, 2027, 2029, 2030, 2031, 2032, 2033, 2034, 2037, 2038, 2050, 2052, 2053, 2054, 2055, 2056, 2057, 2059, 2060, 2062, 2065, 2066, 2067, 2069, 2075, 2076, 2083, 2084, 2090, 2096, 2099, 2100, 2104, 2106, 2110, 2111, 2112, 2119, 2121, 2124, 2125, 2126, 2128, 2129, 2130, 2131, 2134, 2135, 2136, 2137, 2138, 2139, 2143, 2144, 2148, 2149, 2150, 2155, 2156, 2157, 2159, 2160, 2161, 2163, 2164, 2166, 2169, 2177, 2187, 2188, 2189, 2191, 2192, 2194, 2197, 2198, 2199, 2207, 2208, 2209, 2211, 2213, 2214, 2215, 2216, 2219, 2220, 2223, 2226, 2227, 2228, 2229, 2230, 2232, 2242, 2245, 2247, 2248, 2250, 2253, 2258, 2260, 2269, 2275, 2276, 2277, 2279, 2289, 2290, 2291, 2292, 2294, 2296, 2297, 2300, 2302, 2306, 2307, 2308, 2312, 2313, 2314, 2315, 2316, 2324, 2325, 2326, 2327, 2328, 2330, 2333, 2335, 2336, 2337, 2339, 2341, 2342, 2344, 2347, 2349, 2350, 2351, 2356, 2357, 2358, 2361, 2363, 2364, 2366, 2367, 2369, 2370, 2371, 2378, 2380, 2381, 2385, 2387, 2388, 2391, 2394, 2398, 2405, 2406, 2408, 2411, 2413, 2414, 2420, 2421, 2424, 2425, 2427, 2436, 2437, 2438, 2439, 2441, 2442, 2443, 2445, 2446, 2448, 2451, 2458, 2462, 2469, 2472, 2473, 2474, 2475, 2476, 2477, 2480, 2483, 2484]

idx_test4=[4, 11, 13, 15, 2069, 2072, 29, 31, 2080, 2082, 2083, 2084, 38, 36, 42, 57, 58, 2106, 2105, 2110, 66, 2130, 2131, 2135, 2149, 2151, 2170, 2177, 2184, 2208, 2209, 2214, 2218, 2228, 2256, 2275, 2279, 2280, 2283, 2289, 2290, 2291, 2292, 2311, 2313, 2314, 2315, 2326, 2329, 2331, 2334, 2335, 2343, 2344, 2345, 2349, 2360, 2361, 2366, 2370, 2371, 2383, 2385, 2391, 2392, 2393, 2396, 2398, 2402, 2406, 2426, 2431, 2445, 2455, 2469, 2474, 2477, 683, 807, 812, 838, 840, 844, 845, 846, 849, 851, 852, 857, 861, 864, 866, 868, 869, 877, 900, 914, 925, 938, 939, 943, 959, 965, 970, 976, 979, 980, 984, 993, 994, 999, 1002, 1018, 1019, 1035, 1042, 1049, 1050, 1053, 1064, 1067, 1070, 1079, 1085, 1089, 1098, 1105, 1110, 1121, 1133, 1141, 1153, 1154, 1156, 1159, 1161, 1163, 1164, 1169, 1170, 1172, 1176, 1179, 1188, 1189, 1209, 1210, 1234, 1236, 1238, 1253, 1255, 1257, 1258, 1261, 1265, 1271, 1272, 1288, 1295, 1298, 1299, 1307, 1309, 1311, 1313, 1314, 1334, 1336, 1337, 1338, 1340, 1343, 1347, 1348, 1350, 1368, 1371, 1372, 1381, 1382, 1395, 1412, 1413, 1425, 1427, 1430, 1432, 1434, 1443, 1454, 1457, 1465, 1476, 1490, 1491, 1495, 1497, 1503, 1505, 1507, 1508, 1510, 1512, 1523, 1531, 1534, 1558, 1564, 1566, 1567, 1572, 1578, 1586, 1591, 1592, 1601, 1602, 1606, 1622, 1623, 1624, 1628, 1629, 1639, 1651, 1661, 1678, 1688, 1689, 1697, 1716, 1737, 1739, 1746, 1758, 1759, 1760, 1774, 1775, 1778, 1780, 1781, 1783, 1788, 1789, 1814, 1820, 1822, 1823, 1838, 1839, 1840, 1853, 1856, 1865, 1868, 1874, 1877, 1907, 1909, 1920, 1921, 1930, 1939, 1957, 1970, 1972, 1980, 2000, 2001, 2003, 2005, 2007, 2008, 2009, 2012]

idx_test5=[0, 4, 11, 13, 2062, 16, 2065, 2069, 25, 31, 36, 2085, 40, 2089, 41, 42, 45, 46, 48, 2104, 2110, 69, 70, 72, 2121, 2126, 2128, 84, 2136, 2139, 92, 93, 95, 2144, 97, 99, 2148, 102, 111, 113, 2161, 2164, 117, 2166, 126, 127, 2179, 132, 133, 131, 136, 141, 142, 2189, 2194, 148, 149, 151, 152, 2205, 2208, 161, 2211, 164, 168, 170, 2220, 172, 173, 2228, 2229, 180, 183, 184, 185, 181, 188, 2230, 2239, 191, 187, 196, 197, 2247, 203, 209, 2260, 214, 216, 217, 218, 220, 225, 226, 227, 2276, 229, 2278, 235, 236, 2286, 2290, 252, 253, 255, 258, 2307, 2308, 2311, 2312, 2313, 267, 2316, 269, 270, 273, 286, 287, 288, 2338, 2339, 293, 2341, 297, 2347, 2348, 2350, 2351, 305, 309, 2358, 311, 312, 2361, 2363, 2364, 317, 320, 325, 326, 2376, 329, 2378, 337, 340, 341, 343, 2394, 2398, 2399, 2405, 2406, 363, 2414, 2421, 373, 376, 377, 378, 2428, 385, 2436, 389, 2438, 2439, 392, 2441, 2442, 395, 393, 2444, 2445, 399, 2448, 394, 2451, 411, 413, 2462, 415, 2464, 419, 422, 426, 427, 429, 2478, 2480, 433, 434, 436, 441, 446, 464, 472, 479, 486, 490, 499, 501, 505, 509, 510, 511, 513, 517, 518, 520, 523, 527, 534, 537, 542, 546, 549, 552, 557, 567, 571, 587, 595, 599, 603, 604, 611, 613, 618, 625, 626, 629, 640, 648, 652, 658, 659, 661, 664, 667, 668, 669, 670, 681, 687, 694, 696, 701, 702, 704, 705, 710, 715, 717, 719, 722, 727, 729, 730, 734, 746, 747, 748, 758, 760, 764, 773, 782, 787, 791, 797, 823, 826, 828, 829, 834, 835, 840, 841, 842, 847, 852, 860, 862, 871, 876, 878, 900, 909, 911, 912, 915, 926, 935, 947, 951, 969, 975, 976, 992, 1002, 1014, 1029, 1034, 1038, 1040, 1048, 1055, 1060, 1061, 1062, 1077, 1091, 1100, 1104, 1120, 1145, 1147, 1163, 1174, 1184, 1191, 1199, 1201, 1208, 1222, 1228, 1229, 1234, 1238, 1243, 1244, 1256, 1262, 1263, 1264, 1265, 1272, 1275, 1283, 1284, 1295, 1301, 1304, 1305, 1310, 1340, 1345, 1348, 1353, 1356, 1361, 1362, 1376, 1382, 1385, 1388, 1397, 1415, 1423, 1440, 1460, 1478, 1479, 1486, 1489, 1493, 1505, 1506, 1525, 1527, 1537, 1540, 1544, 1549, 1555, 1557, 1566, 1568, 1573, 1576, 1582, 1596, 1604, 1605, 1608, 1617, 1618, 1619, 1624, 1631, 1633, 1635, 1636, 1641, 1648, 1649, 1663, 1670, 1676, 1681, 1682, 1685, 1688, 1691, 1692, 1693, 1697, 1705, 1706, 1725, 1727, 1732, 1750, 1756, 1758, 1761, 1762, 1763, 1767, 1769, 1780, 1786, 1805, 1808, 1812, 1814, 1837, 1844, 1855, 1856, 1865, 1886, 1891, 1892, 1893, 1894, 1895, 1898, 1909, 1910, 1911, 1927, 1931, 1940, 1945, 1948, 1955, 1961, 1967, 1980, 1982, 1988, 1993, 1998, 1999, 2007, 2008, 2012, 2017, 2437, 2027, 2034, 2037]

idx_test6=[2048, 9, 10, 11, 13, 15, 2063, 2066, 20, 2069, 26, 29, 30, 32, 2080, 2082, 2088, 42, 2099, 54, 2104, 2105, 58, 2112, 2113, 2131, 2135, 2153, 2155, 2156, 2166, 2173, 2177, 2184, 2208, 2209, 2214, 2232, 2256, 2260, 2268, 2274, 2275, 2276, 2283, 2284, 2286, 2289, 2292, 2296, 2299, 2311, 2326, 2331, 2343, 2344, 2345, 2349, 2352, 2360, 2371, 2381, 2391, 2393, 2394, 2398, 2399, 2406, 2421, 2425, 2426, 2467, 2468, 640, 683, 804, 807, 811, 812, 819, 820, 833, 836, 838, 839, 840, 841, 842, 844, 846, 849, 851, 852, 855, 860, 861, 862, 864, 866, 868, 869, 876, 877, 892, 904, 914, 919, 924, 925, 930, 943, 945, 959, 969, 970, 975, 976, 980, 987, 998, 1000, 1002, 1012, 1020, 1021, 1023, 1032, 1046, 1053, 1064, 1069, 1076, 1082, 1083, 1087, 1088, 1099, 1104, 1105, 1110, 1117, 1119, 1130, 1132, 1133, 1140, 1153, 1154, 1156, 1159, 1160, 1163, 1164, 1169, 1170, 1172, 1175, 1179, 1184, 1185, 1189, 1234, 1235, 1236, 1238, 1244, 1255, 1256, 1257, 1265, 1271, 1272, 1280, 1281, 1288, 1291, 1298, 1299, 1300, 1301, 1309, 1311, 1313, 1324, 1331, 1334, 1336, 1338, 1339, 1340, 1347, 1348, 1350, 1366, 1368, 1372, 1382, 1386, 1397, 1410, 1411, 1412, 1413, 1425, 1430, 1433, 1434, 1443, 1454, 1465, 1476, 1482, 1489, 1497, 1499, 1500, 1501, 1503, 1505, 1507, 1508, 1511, 1512, 1513, 1523, 1527, 1531, 1535, 1536, 1540, 1544, 1549, 1558, 1564, 1566, 1576, 1581, 1586, 1596, 1601, 1604, 1606, 1613, 1622, 1623, 1624, 1635, 1639, 1651, 1656, 1669, 1676, 1688, 1701, 1703, 1716, 1746, 1756, 1759, 1773, 1775, 1778, 1780, 1781, 1782, 1783, 1787, 1788, 1789, 1811, 1814, 1820, 1822, 1823, 1837, 1839, 1853, 1854, 1863, 1868, 1877, 1886, 1898, 1901, 1907, 1909, 1922, 1930, 1931, 1934, 1939, 1948, 1949, 1950, 1956, 1962, 1977, 1980, 1981, 1982, 1992, 2003, 2007, 2008, 2013, 2015, 2027, 2038]
#print("adj.shape[0]",adj.shape[0])
idx_test7=[2048, 9, 13, 15, 2063, 20, 30, 32, 2080, 2082, 2088, 2105, 2113, 2153, 2173, 2184, 2256, 2268, 2274, 2283, 2284, 2299, 2311, 2331, 2343, 2345, 2352, 2360, 2393, 2399, 2426, 2467, 2468, 640, 683, 807, 812, 819, 820, 833, 839, 846, 851, 855, 861, 864, 904, 925, 943, 959, 970, 998, 1012, 1020, 1021, 1023, 1046, 1076, 1082, 1083, 1088, 1105, 1110, 1117, 1140, 1154, 1159, 1170, 1175, 1179, 1185, 1189, 1236, 1255, 1280, 1281, 1288, 1291, 1299, 1300, 1311, 1313, 1324, 1331, 1336, 1338, 1339, 1350, 1368, 1386, 1410, 1411, 1412, 1413, 1430, 1443, 1454, 1476, 1482, 1497, 1500, 1501, 1503, 1507, 1512, 1513, 1523, 1531, 1549, 1581, 1586, 1606, 1622, 1669, 1703, 1716, 1775, 1781, 1782, 1783, 1788, 1789, 1811, 1853, 1854, 1868, 1901, 1934, 1939, 1962, 1977, 1980, 2015]

#idx_test8=[13, 15, 2072, 2080, 2082, 57, 2105, 66, 2151, 2170, 2184, 2256, 2280, 2283, 2311, 2329, 2331, 2334, 2343, 2345, 2360, 2383, 2392, 2393, 2396, 2402, 2426, 2431, 2455, 683, 807, 812, 846, 851, 861, 864, 925, 943, 959, 970, 984, 1035, 1042, 1050, 1070, 1079, 1089, 1098, 1105, 1110, 1121, 1141, 1154, 1159, 1170, 1179, 1189, 1210, 1236, 1253, 1255, 1258, 1261, 1288, 1299, 1307, 1311, 1313, 1336, 1338, 1343, 1350, 1368, 1371, 1381, 1412, 1413, 1430, 1443, 1454, 1476, 1495, 1497, 1503, 1507, 1510, 1512, 1523, 1531, 1534, 1567, 1572, 1578, 1586, 1591, 1592, 1606, 1622, 1689, 1716, 1737, 1739, 1775, 1781, 1783, 1788, 1789, 1853, 1868, 1921, 1939, 1957, 1970, 1972, 1980, 2005]

idx_test8=[0, 2050, 2057, 2059, 2060, 16, 2065, 21, 39, 40, 41, 2090, 43, 45, 49, 53, 56, 69, 2116, 2124, 2128, 2129, 80, 85, 86, 87, 2137, 2138, 91, 2140, 2143, 95, 2147, 99, 102, 103, 2157, 2159, 2161, 2162, 114, 2164, 118, 2167, 2168, 2169, 123, 125, 126, 128, 132, 139, 2187, 141, 2189, 143, 145, 2194, 2191, 2197, 151, 2199, 2201, 2198, 154, 2205, 2211, 164, 2219, 171, 173, 2220, 2223, 177, 2226, 2229, 184, 187, 188, 189, 2241, 2242, 196, 2244, 197, 200, 202, 2250, 203, 210, 214, 2263, 216, 215, 225, 226, 229, 2278, 230, 232, 233, 235, 240, 243, 245, 244, 2294, 253, 254, 256, 2306, 2307, 2308, 260, 258, 262, 264, 266, 267, 268, 269, 271, 273, 274, 275, 2325, 281, 2332, 2333, 284, 287, 288, 2338, 2339, 296, 297, 299, 2351, 303, 304, 308, 310, 311, 312, 313, 314, 2362, 2364, 316, 2369, 324, 326, 2376, 331, 2380, 334, 337, 339, 341, 343, 347, 348, 355, 362, 2411, 2413, 369, 370, 371, 2420, 2427, 2429, 385, 388, 2437, 390, 393, 2441, 395, 2444, 397, 398, 399, 2448, 2449, 403, 406, 407, 412, 2462, 415, 414, 418, 423, 424, 2472, 426, 2475, 429, 2478, 430, 433, 2483, 2484, 442, 445, 447, 449, 456, 461, 464, 473, 474, 476, 477, 479, 481, 484, 487, 498, 509, 511, 513, 517, 520, 525, 528, 530, 531, 533, 534, 537, 538, 542, 544, 546, 557, 566, 585, 588, 590, 595, 600, 602, 603, 607, 609, 610, 613, 614, 615, 626, 644, 647, 648, 652, 658, 659, 661, 665, 666, 669, 670, 672, 673, 674, 679, 684, 689, 691, 696, 698, 701, 702, 705, 707, 711, 715, 717, 718, 719, 720, 724, 727, 729, 735, 147, 748, 756, 764, 766, 768, 777, 778, 779, 788, 2192, 794, 795, 797, 805, 816, 828, 829, 830, 834, 835, 847, 856, 859, 872, 879, 883, 887, 896, 911, 912, 915, 916, 946, 947, 948, 951, 958, 968, 973, 977, 981, 992, 996, 1001, 1004, 1015, 1016, 1029, 1034, 1039, 1048, 1051, 1060, 1061, 1071, 1091, 1092, 1100, 1101, 1120, 1122, 1131, 1134, 1145, 1147, 1148, 1149, 1158, 1168, 1174, 1187, 1201, 1219, 1224, 1225, 1226, 1228, 1229, 1239, 1240, 1243, 1245, 1246, 1260, 1262, 1263, 1264, 1266, 1269, 1274, 1278, 1282, 1283, 1284, 1292, 1305, 1319, 1330, 1353, 1361, 1376, 1384, 1385, 1388, 1405, 1407, 1409, 1415, 1435, 1438, 1440, 1441, 1442, 1446, 1447, 1461, 1468, 1478, 1479, 1494, 1506, 1516, 1518, 1525, 1537, 1541, 1543, 1546, 1550, 1555, 1562, 1573, 1575, 1585, 1587, 1588, 1605, 1608, 1609, 1614, 1616, 1617, 1618, 1619, 1620, 1621, 1626, 1631, 1634, 1636, 1642, 1662, 1670, 1675, 1679, 1681, 1685, 1690, 1692, 1693, 1694, 1695, 1702, 1705, 1706, 1708, 1709, 1710, 1719, 1720, 1725, 1727, 1740, 1749, 1750, 1762, 1763, 1767, 1769, 1808, 1830, 1833, 1834, 1835, 1844, 1845, 1846, 1847, 1862, 1866, 1878, 1880, 1882, 1891, 1892, 1893, 1894, 1895, 1897, 1899, 1911, 1918, 1919, 1926, 1940, 1944, 1961, 1966, 1988, 1993, 1995, 1998, 1999, 2004, 2016, 2017, 2024, 2032, 2033, 2037]

idx_test=np.array(idx_test8)

#idx_test=idx_test1

idx_unlabeled = np.union1d(idx_val, idx_test)



perturbations = int(args.ptb_rate * (adj.sum()//2))

adj, features, labels = preprocess(adj, features, labels, preprocess_adj=False)



# set up attack model
if 'Self' in args.model:
    lambda_ = 0
if 'Train' in args.model:
    lambda_ = 1
if 'Both' in args.model:
    lambda_ = 0.5

if 'A' in args.model:
    model = MetaApprox(nfeat=features.shape[1], hidden_sizes=[args.hidden],
                       nnodes=adj.shape[0], nclass=nclass, dropout=0.5,
                       train_iters=100, attack_features=False, lambda_=lambda_, device=device)

else:
    model = Metattack(nfeat=features.shape[1], hidden_sizes=[args.hidden],
                       nnodes=adj.shape[0], nclass=nclass, dropout=0.5,
                       train_iters=100, attack_features=False, lambda_=lambda_, device=device)

if device != 'cpu':
    adj = adj.to(device)
    features = features.to(device)
    labels = labels.to(device)
    model = model.to(device)


def test(adj):
    ''' test on HITSGNN '''

    adj = normalize_adj_tensor(adj)
    hitsgnn = HITSGNN(nfeat=features.shape[1],
              nhid=args.hidden,
              nclass=labels.max().item() + 1,
              dropout=0.5)

    if device != 'cpu':
        hitsgnn = hitsgnn.to(device)

    optimizer = optim.Adam(hitsgnn.parameters(),
                           lr=args.lr, weight_decay=5e-4)

    hitsgnn.train()

    for epoch in range(args.epochs):
        optimizer.zero_grad()
        output = hitsgnn(features, adj)
        loss_train = F.nll_loss(output[idx_train], labels[idx_train])
        acc_train = accuracy(output[idx_train], labels[idx_train])
        loss_train.backward()
        optimizer.step()

    hitsgnn.eval()
    output = hitsgnn(features, adj)


    loss_test = F.nll_loss(output[idx_test], labels[idx_test])
    acc_test = accuracy(output[idx_test], labels[idx_test])


    # print("Test set results:",
    #       "loss= {:.4f}".format(loss_test.item()),
    #       "accuracy= {:.4f}".format(acc_test.item()))

    return acc_test.item()


def main():

    acc = []
    runs = 1
    
    for i in range(runs):
        acc.append(test(adj))

    torch.cuda.empty_cache()

    #for i in range(3):
    
    modified_adj = model(features, adj, labels, idx_train,
                            idx_unlabeled, perturbations, ll_constraint=False)
    modified_adj = modified_adj.detach()

    for i in range(runs):
        acc.append(test(modified_adj))

    print("acc",acc)



    #data=pd.DataFrame({"Acc. Clean":clean_acc,"Acc. Perturbed":attacked_acc})

    #plt.figure(figsize=(6,6))
    #sns.boxplot(data=data)#, re_trainings*[accuracy_logistic]])

    #plt.title("Accuracy before/after perturbing {}% edges using model {}".format(args.ptb_rate*100, args.model))
    #plt.savefig("results_on_{}.png".format(args.dataset), dpi=600)
    #plt.show()


if __name__ == '__main__':
    main()

#neighbor type 0:
#acc [0.801307847082495, 0.6916498993963783, 0.6383299798792758, 0.5900402414486922]

#neighbor type 1:
#acc [0.7979797979797979, 0.7272727272727273, 0.7272727272727273, 0.734006734006734]

#neighbor type 2:
#acc [0.8106382978723404, 0.7425531914893617, 0.7297872340425532, 0.7191489361702128]

#neighbor type 3:
#acc [0.8111769686706181, 0.720575783234547, 0.6545300592718035, 0.6054191363251482]

#neighbor type 4:
#acc [0.8158844765342961, 0.8050541516245487, 0.779783393501805, 0.7833935018050542]

#neighbor type 5:
#acc [0.8376623376623377, 0.7489177489177489, 0.7575757575757576, 0.7445887445887446]

#neighbor type 6:
#acc [0.8084415584415585, 0.814935064935065, 0.8181818181818182, 0.8181818181818182]

#neighbor type 7:
#acc [0.8270676691729323, 0.8045112781954886, 0.7819548872180451, 0.7744360902255638]

#neighbor type 8:
#acc [0.8362068965517241, 0.8189655172413793, 0.7586206896551724, 0.7241379310344828]

#neighbor type 8-0:
#acc [0.7948717948717949, 0.7061143984220908,  0.7120315581854044, 0.717948717948718]



