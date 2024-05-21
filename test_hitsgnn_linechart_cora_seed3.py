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
parser.add_argument('--seed', type=int, default=17, help='Random seed.')
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



idx_test1=[6, 2055, 2057, 10, 2059, 2060, 2062, 14, 2073, 26, 2075, 2085, 38, 39, 2089, 44, 46, 51, 52, 53, 56, 58, 59, 60, 64, 69, 2117, 2116, 2121, 74, 2124, 77, 2127, 79, 83, 84, 85, 2133, 87, 2136, 2138, 92, 2142, 2143, 96, 94, 99, 2148, 2152, 110, 2159, 112, 116, 2164, 118, 2167, 2168, 2169, 124, 2172, 125, 2177, 2178, 132, 133, 135, 2187, 2188, 142, 141, 2192, 145, 146, 148, 143, 151, 144, 154, 2202, 2205, 157, 2209, 161, 165, 2215, 2216, 2218, 171, 172, 174, 2224, 177, 2226, 179, 2228, 181, 187, 188, 189, 191, 2241, 196, 199, 200, 203, 2248, 2257, 210, 211, 2260, 2261, 214, 216, 218, 221, 222, 226, 229, 230, 232, 233, 235, 2285, 241, 243, 244, 245, 2294, 247, 251, 2300, 256, 258, 2306, 260, 262, 263, 268, 269, 271, 276, 2326, 2327, 283, 2332, 2333, 285, 286, 289, 2338, 2339, 293, 299, 2348, 301, 302, 2353, 308, 309, 312, 313, 2369, 325, 2375, 328, 329, 2380, 332, 334, 2382, 2384, 337, 338, 339, 2386, 343, 344, 2394, 2395, 347, 353, 2403, 355, 357, 2408, 362, 369, 371, 2420, 372, 374, 375, 2427, 2428, 380, 2433, 388, 393, 2444, 398, 2446, 2450, 402, 403, 406, 410, 412, 2462, 418, 420, 423, 424, 2472, 2475, 429, 430, 432, 2482, 2483, 2484, 438, 441, 445, 447, 452, 456, 460, 461, 470, 479, 483, 484, 489, 493, 496, 497, 498, 505, 509, 511, 512, 513, 520, 522, 525, 526, 534, 537, 542, 544, 546, 547, 557, 564, 572, 586, 588, 590, 591, 592, 595, 596, 597, 600, 602, 609, 610, 612, 616, 617, 618, 626, 627, 633, 641, 644, 645, 649, 652, 654, 658, 659, 2166, 661, 669, 670, 675, 679, 682, 684, 685, 689, 691, 696, 698, 699, 702, 704, 140, 717, 720, 725, 738, 739, 740, 744, 747, 748, 749, 750, 752, 754, 757, 759, 764, 769, 778, 780, 782, 785, 787, 790, 792, 795, 797, 798, 805, 811, 821, 830, 836, 840, 845, 852, 859, 860, 866, 876, 879, 885, 889, 890, 891, 893, 899, 900, 911, 912, 915, 916, 922, 924, 938, 940, 946, 948, 949, 951, 958, 968, 969, 974, 976, 977, 981, 986, 993, 1003, 1004, 1009, 1015, 1025, 1027, 1029, 1032, 1039, 1057, 1068, 1080, 1084, 1085, 1092, 1096, 1099, 1100, 1103, 1104, 1109, 1119, 1120, 1123, 1131, 1133, 1134, 1143, 1148, 1149, 1151, 1152, 1153, 1156, 1158, 1165, 1172, 1176, 1186, 1187, 1188, 1195, 1197, 1201, 1206, 1207, 1212, 1224, 1225, 1229, 1238, 1239, 1240, 1243, 1249, 1254, 1260, 1262, 1263, 1268, 1269, 1283, 1309, 1319, 1340, 1343, 1361, 1362, 1363, 1370, 1376, 1384, 1385, 1388, 1391, 1392, 1394, 1396, 1397, 1399, 1405, 1406, 1407, 1409, 1415, 1417, 1418, 1419, 1435, 1438, 1447, 1455, 1459, 1460, 1463, 1465, 1467, 1468, 1471, 1472, 1474, 1489, 1491, 1492, 1498, 1499, 1502, 1505, 1518, 1520, 1535, 1538, 1542, 1543, 1546, 1547, 1550, 1552, 1561, 1565, 1569, 1570, 1573, 1579, 1587, 1591, 1594, 1603, 1605, 1607, 1608, 1609, 1611, 1614, 1617, 1618, 1621, 1626, 1630, 1631, 1642, 1643, 1649, 1662, 1666, 1673, 1679, 1682, 1683, 1690, 1692, 1698, 1702, 1705, 1709, 1725, 1736, 1740, 1750, 1759, 1761, 1763, 1765, 1766, 1767, 1769, 1770, 1783, 1786, 1792, 1801, 1805, 1806, 1809, 1828, 1830, 1834, 1835, 1838, 1840, 1842, 1845, 1863, 1865, 1866, 1867, 1876, 1881, 1882, 1885, 1892, 1893, 1894, 1909, 1911, 1919, 1920, 1926, 1927, 1929, 1932, 1936, 1944, 1945, 1946, 1949, 1953, 1960, 1979, 1984, 1990, 1998, 1999, 2000, 2003, 2004, 2006, 2007, 2008, 2009, 2011, 2013, 2016, 2025, 2026, 2027, 2028, 2032, 2037, 2044]

idx_test2=[4, 5, 2052, 7, 8, 10, 2053, 2054, 13, 14, 15, 2064, 16, 2060, 3, 2073, 26, 27, 2077, 38, 42, 43, 45, 44, 49, 2103, 56, 58, 59, 60, 62, 11, 2107, 65, 67, 2126, 2127, 2131, 2132, 2136, 2137, 2138, 2143, 2150, 2155, 2163, 2166, 2167, 2168, 2170, 2172, 2173, 2174, 2177, 2178, 2180, 2184, 2185, 2186, 2218, 2220, 2228, 2236, 2238, 2240, 2243, 2244, 2245, 2256, 2264, 2265, 2276, 2278, 2279, 2283, 2295, 2300, 2303, 2305, 2306, 2311, 2313, 2326, 2332, 2340, 2341, 2344, 2346, 2358, 2362, 2365, 2366, 2370, 2371, 2374, 2379, 2380, 2384, 2390, 2392, 2394, 2396, 2399, 2403, 2406, 2411, 2416, 2418, 2428, 2431, 2432, 2446, 2447, 2467, 422, 2474, 2482, 2484, 638, 811, 812, 817, 832, 833, 836, 837, 840, 844, 845, 851, 852, 861, 862, 864, 866, 876, 877, 879, 882, 896, 897, 898, 900, 901, 904, 906, 916, 917, 925, 929, 938, 940, 941, 942, 944, 945, 952, 954, 960, 968, 969, 978, 979, 981, 989, 991, 1002, 1005, 1007, 1012, 1015, 1016, 1020, 1021, 1022, 1023, 1024, 1039, 1041, 1049, 1052, 1053, 1061, 1062, 1065, 1071, 1074, 1080, 1083, 1088, 1092, 1098, 1099, 1104, 1105, 1108, 1109, 1110, 1111, 1115, 1119, 1122, 1123, 1131, 1132, 1133, 1135, 1140, 1144, 1149, 1150, 1151, 1157, 1158, 1166, 1169, 1170, 1172, 1175, 1176, 1177, 1179, 1180, 1182, 1184, 1188, 1189, 1192, 1193, 1209, 1220, 1221, 1225, 1229, 1231, 1232, 1234, 1236, 1238, 1241, 1242, 1247, 1254, 1255, 1257, 1260, 1263, 1265, 1280, 1282, 1288, 1291, 1297, 1298, 1299, 1300, 1303, 1311, 1317, 1320, 1325, 1326, 1327, 1332, 1335, 1338, 1339, 1340, 1347, 1348, 1352, 1354, 1361, 1366, 1370, 1373, 1374, 1375, 1379, 1380, 1388, 1391, 1392, 1394, 1396, 1397, 1398, 1399, 1403, 1405, 1410, 1412, 1416, 1418, 1420, 1430, 1435, 1436, 1440, 1443, 1451, 1454, 1457, 1460, 1462, 1464, 1465, 1467, 1476, 1478, 1479, 1480, 1482, 1489, 1491, 1492, 1493, 1495, 1497, 1499, 1502, 1505, 1507, 1508, 1509, 1510, 1513, 1521, 1523, 1526, 1534, 1535, 1540, 1542, 1543, 1553, 1560, 1564, 1565, 1569, 1570, 1572, 1576, 1578, 1579, 1581, 1588, 1597, 1601, 1602, 1608, 1609, 1611, 1612, 1622, 1637, 1644, 1647, 1651, 1667, 1670, 1672, 1677, 1678, 1687, 1688, 1689, 1707, 1709, 1710, 1715, 1717, 1719, 1720, 1721, 1727, 1730, 1731, 1732, 1733, 1736, 1737, 1739, 1751, 1754, 1757, 1761, 1763, 1766, 1767, 1773, 1776, 1783, 1788, 1792, 1796, 1797, 1801, 1802, 1804, 1806, 1809, 1811, 1813, 1820, 1823, 1824, 1828, 1835, 1839, 1842, 1845, 1847, 1853, 1854, 1863, 1864, 1865, 1867, 1868, 1870, 1878, 1883, 1887, 1892, 1893, 1894, 1896, 1898, 1920, 1949, 1960, 1973, 1974, 1976, 1982, 1989, 1990, 1993, 1994, 1998, 2000, 2001, 2003, 2004, 2005, 2007, 2008, 2009, 2010, 2013, 2032, 2036, 2044, 2047]

idx_test3=[0, 3, 4, 5, 6, 10, 11, 14, 15, 16, 19, 21, 22, 25, 26, 31, 33, 35, 37, 38, 39, 40, 41, 42, 43, 45, 47, 48, 49, 50, 52, 53, 56, 58, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 75, 76, 78, 79, 80, 84, 85, 87, 89, 92, 94, 95, 101, 103, 104, 107, 110, 112, 113, 115, 118, 120, 122, 125, 126, 127, 132, 133, 134, 136, 138, 140, 141, 142, 143, 144, 145, 146, 150, 151, 152, 153, 154, 156, 161, 163, 165, 166, 167, 171, 177, 179, 181, 182, 185, 187, 188, 189, 191, 192, 193, 196, 198, 200, 203, 204, 205, 207, 210, 211, 212, 217, 218, 220, 221, 222, 223, 229, 230, 232, 235, 236, 242, 244, 246, 247, 250, 252, 253, 255, 256, 257, 258, 261, 262, 263, 264, 266, 267, 268, 269, 271, 272, 273, 275, 276, 278, 279, 280, 283, 285, 286, 287, 289, 291, 293, 296, 299, 300, 301, 302, 305, 306, 309, 312, 313, 315, 317, 318, 321, 322, 324, 326, 329, 330, 334, 335, 337, 338, 340, 343, 344, 345, 347, 351, 353, 355, 357, 360, 361, 363, 365, 366, 367, 368, 369, 370, 371, 374, 375, 382, 384, 385, 386, 388, 389, 392, 394, 395, 398, 402, 404, 406, 408, 409, 410, 411, 412, 416, 418, 419, 420, 421, 422, 423, 424, 425, 427, 429, 430, 432, 434, 436, 438, 441, 444, 445, 446, 447, 449, 451, 454, 455, 457, 461, 464, 469, 470, 471, 472, 478, 482, 483, 484, 486, 487, 490, 495, 496, 497, 498, 502, 505, 508, 509, 511, 512, 513, 514, 517, 518, 519, 520, 521, 522, 523, 525, 526, 527, 532, 534, 535, 537, 538, 539, 540, 541, 542, 546, 547, 548, 549, 550, 551, 552, 554, 555, 556, 568, 572, 575, 577, 582, 586, 588, 590, 591, 593, 595, 596, 597, 598, 599, 600, 601, 603, 604, 605, 608, 610, 611, 612, 614, 615, 616, 617, 619, 620, 622, 624, 625, 626, 627, 628, 629, 632, 633, 635, 636, 641, 643, 644, 645, 648, 652, 654, 655, 658, 660, 661, 666, 668, 669, 670, 673, 675, 676, 678, 684, 685, 689, 691, 692, 693, 694, 696, 698, 699, 702, 704, 705, 708, 712, 713, 717, 720, 722, 725, 727, 728, 729, 732, 734, 735, 738, 739, 742, 743, 744, 745, 746, 747, 748, 750, 751, 752, 753, 754, 757, 759, 766, 769, 770, 771, 772, 773, 775, 780, 783, 787, 790, 792, 793, 795, 796, 797, 798, 800, 801, 809, 811, 817, 818, 821, 826, 828, 829, 830, 832, 834, 840, 843, 844, 851, 860, 862, 863, 866, 867, 876, 877, 879, 888, 890, 891, 893, 894, 898, 899, 900, 903, 906, 909, 916, 922, 924, 926, 927, 932, 934, 935, 937, 938, 940, 946, 948, 949, 951, 956, 960, 964, 965, 968, 969, 974, 976, 977, 979, 981, 986, 990, 993, 996, 997, 1003, 1004, 1005, 1007, 1009, 1011, 1014, 1015, 1016, 1018, 1025, 1027, 1029, 1032, 1034, 1036, 1038, 1040, 1043, 1047, 1053, 1057, 1059, 1060, 1061, 1067, 1068, 1071, 1075, 1080, 1085, 1087, 1092, 1094, 1096, 1099, 1100, 1103, 1104, 1105, 1106, 1109, 1112, 1119, 1120, 1122, 1125, 1129, 1130, 1131, 1132, 1133, 1134, 1139, 1140, 1143, 1144, 1149, 1151, 1153, 1158, 1165, 1166, 1167, 1169, 1172, 1175, 1176, 1178, 1179, 1182, 1184, 1186, 1188, 1190, 1191, 1192, 1193, 1194, 1195, 1196, 1197, 1200, 1201, 1206, 1207, 1209, 1212, 1213, 1214, 1215, 1218, 1222, 1223, 1224, 1228, 1238, 1239, 1240, 1242, 1243, 1244, 1248, 1249, 1254, 1257, 1260, 1262, 1263, 1267, 1268, 1269, 1272, 1273, 1275, 1277, 1282, 1283, 1287, 1288, 1292, 1298, 1301, 1303, 1306, 1309, 1310, 1314, 1317, 1319, 1320, 1322, 1324, 1333, 1337, 1340, 1345, 1346, 1347, 1348, 1357, 1361, 1362, 1363, 1364, 1365, 1366, 1370, 1372, 1373, 1375, 1376, 1377, 1378, 1382, 1384, 1385, 1388, 1389, 1391, 1392, 1394, 1396, 1399, 1405, 1406, 1407, 1409, 1419, 1421, 1423, 1427, 1432, 1434, 1435, 1438, 1439, 1440, 1442, 1445, 1447, 1448, 1450, 1451, 1453, 1455, 1457, 1460, 1463, 1465, 1466, 1468, 1472, 1474, 1476, 1478, 1479, 1480, 1485, 1486, 1489, 1491, 1493, 1494, 1498, 1499, 1505, 1506, 1508, 1516, 1517, 1518, 1520, 1521, 1525, 1527, 1528, 1530, 1535, 1538, 1539, 1540, 1542, 1543, 1544, 1546, 1547, 1549, 1551, 1555, 1556, 1557, 1558, 1559, 1561, 1564, 1569, 1570, 1573, 1575, 1576, 1579, 1580, 1585, 1586, 1587, 1588, 1591, 1592, 1596, 1597, 1601, 1602, 1603, 1604, 1609, 1611, 1612, 1613, 1614, 1616, 1617, 1618, 1621, 1625, 1628, 1629, 1630, 1631, 1634, 1635, 1640, 1641, 1642, 1643, 1646, 1647, 1649, 1651, 1652, 1653, 1655, 1657, 1661, 1662, 1666, 1667, 1670, 1675, 1678, 1679, 1681, 1683, 1684, 1687, 1690, 1691, 1692, 1697, 1698, 1705, 1706, 1708, 1709, 1710, 1713, 1715, 1719, 1721, 1725, 1727, 1732, 1736, 1740, 1742, 1748, 1750, 1752, 1754, 1756, 1759, 1761, 1763, 1764, 1765, 1766, 1767, 1769, 1773, 1774, 1778, 1780, 1783, 1786, 1787, 1791, 1793, 1796, 1801, 1803, 1805, 1808, 1809, 1812, 1814, 1816, 1819, 1820, 1822, 1823, 1826, 1828, 1830, 1834, 1835, 1837, 1840, 1841, 1851, 1855, 1856, 1858, 1859, 1860, 1861, 1862, 1865, 1867, 1871, 1872, 1873, 1874, 1875, 1877, 1878, 1879, 1880, 1882, 1884, 1885, 1886, 1889, 1891, 1892, 1893, 1894, 1901, 1902, 1905, 1907, 1909, 1910, 1911, 1919, 1920, 1922, 1923, 1924, 1925, 1926, 1927, 1930, 1932, 1936, 1938, 1940, 1941, 1944, 1945, 1947, 1949, 1950, 1953, 1954, 1955, 1956, 1960, 1963, 1970, 1974, 1978, 1979, 1982, 1983, 1984, 1986, 1987, 1989, 1990, 1993, 1995, 1999, 2000, 2002, 2003, 2004, 2006, 2007, 2008, 2009, 2011, 2013, 2017, 2019, 2020, 2021, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2037, 2044, 2052, 2053, 2054, 2055, 2056, 2057, 2059, 2060, 2062, 2066, 2067, 2069, 2073, 2074, 2075, 2079, 2083, 2084, 2085, 2100, 2103, 2106, 2109, 2115, 2117, 2119, 2121, 2124, 2126, 2127, 2134, 2135, 2136, 2137, 2138, 2139, 2141, 2143, 2144, 2148, 2149, 2150, 2152, 2155, 2159, 2161, 2163, 2164, 2166, 2169, 2172, 2177, 2178, 2179, 2185, 2187, 2188, 2189, 2191, 2192, 2195, 2197, 2198, 2199, 2200, 2201, 2202, 2203, 2205, 2211, 2213, 2215, 2216, 2220, 2222, 2223, 2224, 2226, 2228, 2230, 2232, 2234, 2235, 2239, 2240, 2245, 2248, 2254, 2257, 2258, 2260, 2261, 2265, 2277, 2279, 2281, 2285, 2287, 2290, 2291, 2293, 2294, 2296, 2300, 2305, 2306, 2308, 2311, 2313, 2314, 2315, 2316, 2318, 2319, 2320, 2322, 2323, 2326, 2327, 2328, 2333, 2335, 2336, 2337, 2339, 2341, 2342, 2344, 2347, 2351, 2353, 2358, 2361, 2366, 2368, 2369, 2370, 2375, 2376, 2380, 2382, 2384, 2385, 2386, 2387, 2388, 2390, 2394, 2395, 2403, 2406, 2408, 2411, 2415, 2420, 2424, 2427, 2428, 2432, 2433, 2434, 2436, 2437, 2438, 2439, 2441, 2442, 2444, 2445, 2446, 2448, 2450, 2451, 2458, 2459, 2462, 2463, 2467, 2469, 2470, 2471, 2472, 2473, 2474, 2475, 2476, 2478, 2480, 2482, 2483, 2484]

idx_test4=[11, 13, 14, 15, 2064, 2069, 2073, 2077, 31, 32, 2082, 37, 38, 42, 43, 2103, 56, 2106, 65, 2131, 2136, 2142, 2149, 2151, 2164, 2166, 2170, 2177, 2178, 2184, 2185, 2204, 2213, 2228, 2237, 2244, 2245, 2256, 2260, 2261, 2278, 2279, 2281, 2286, 2287, 2290, 2291, 2311, 2313, 2314, 2315, 2318, 2320, 2321, 2322, 2326, 2334, 2335, 2346, 2358, 2359, 2360, 2361, 2365, 2366, 2370, 2371, 2372, 2375, 2385, 2390, 2392, 2396, 2398, 2399, 2406, 2411, 2424, 2428, 2445, 2469, 2484, 619, 640, 812, 817, 844, 851, 852, 866, 869, 870, 877, 879, 900, 906, 917, 925, 929, 930, 931, 933, 934, 938, 939, 942, 943, 944, 953, 959, 965, 970, 976, 983, 1005, 1039, 1040, 1041, 1080, 1085, 1110, 1133, 1150, 1153, 1156, 1169, 1170, 1172, 1177, 1179, 1182, 1184, 1185, 1188, 1192, 1193, 1209, 1210, 1234, 1236, 1238, 1239, 1240, 1254, 1255, 1257, 1258, 1263, 1272, 1273, 1281, 1282, 1287, 1288, 1299, 1314, 1338, 1340, 1343, 1346, 1347, 1348, 1351, 1361, 1364, 1370, 1373, 1376, 1382, 1385, 1394, 1396, 1409, 1411, 1414, 1420, 1427, 1430, 1435, 1443, 1445, 1454, 1464, 1465, 1467, 1476, 1480, 1484, 1493, 1494, 1495, 1497, 1499, 1503, 1505, 1508, 1509, 1510, 1513, 1523, 1533, 1539, 1544, 1549, 1558, 1570, 1572, 1576, 1578, 1579, 1581, 1585, 1586, 1591, 1597, 1601, 1606, 1608, 1622, 1643, 1650, 1651, 1667, 1678, 1688, 1689, 1690, 1700, 1709, 1710, 1730, 1731, 1735, 1766, 1773, 1778, 1780, 1781, 1783, 1788, 1792, 1793, 1797, 1814, 1820, 1823, 1828, 1836, 1838, 1856, 1858, 1864, 1865, 1871, 1877, 1883, 1894, 1908, 1920, 1949, 1976, 1993, 2000, 2003, 2005, 2007, 2008, 2013, 2043, 2044, 2045]

idx_test5=[4, 5, 6, 2052, 8, 2053, 10, 11, 2054, 2055, 14, 2069, 22, 27, 2075, 2079, 39, 2087, 41, 46, 49, 2102, 56, 2106, 59, 60, 67, 2115, 69, 2117, 74, 78, 77, 2134, 2136, 2137, 2138, 2139, 92, 2143, 2144, 2148, 112, 117, 2172, 124, 126, 127, 132, 134, 136, 2187, 140, 143, 145, 148, 2198, 151, 152, 2201, 2202, 156, 2205, 162, 165, 167, 2215, 170, 174, 177, 179, 180, 2228, 2230, 187, 188, 189, 196, 2248, 203, 2254, 207, 2260, 2261, 214, 216, 2265, 218, 2270, 223, 226, 229, 2277, 2279, 235, 2285, 243, 245, 246, 247, 251, 252, 253, 255, 256, 2305, 260, 261, 262, 269, 275, 2326, 278, 281, 283, 2333, 286, 2339, 2341, 295, 296, 2344, 2348, 302, 2351, 2353, 306, 313, 315, 318, 2368, 2371, 324, 328, 2376, 2382, 334, 2384, 343, 344, 346, 2394, 349, 353, 2403, 355, 357, 2406, 2411, 2415, 382, 2433, 2439, 393, 398, 2446, 2450, 2452, 406, 410, 411, 2462, 2463, 420, 2469, 422, 421, 2472, 2473, 427, 431, 2480, 2482, 2481, 436, 438, 439, 441, 444, 446, 453, 460, 469, 470, 471, 483, 486, 488, 490, 498, 517, 527, 529, 534, 542, 546, 547, 548, 549, 550, 552, 554, 559, 574, 588, 595, 597, 599, 600, 604, 608, 611, 615, 616, 617, 618, 622, 626, 627, 635, 641, 643, 645, 658, 660, 666, 669, 670, 675, 686, 688, 690, 692, 702, 716, 717, 738, 742, 744, 745, 749, 752, 761, 769, 775, 776, 777, 782, 790, 797, 818, 830, 836, 840, 843, 844, 845, 866, 882, 889, 909, 916, 922, 948, 951, 968, 974, 981, 985, 987, 992, 1009, 1014, 1015, 1029, 1034, 1036, 1038, 1040, 1043, 1047, 1053, 1059, 1062, 1068, 1071, 1096, 1099, 1105, 1122, 1123, 1125, 1131, 1133, 1134, 1144, 1176, 1178, 1182, 1184, 1197, 1207, 1225, 1229, 1238, 1242, 1258, 1263, 1266, 1272, 1286, 1298, 1303, 1317, 1332, 1337, 1340, 1361, 1362, 1370, 1373, 1376, 1384, 1389, 1405, 1406, 1415, 1417, 1418, 1419, 1424, 1435, 1447, 1455, 1459, 1460, 1462, 1463, 1465, 1479, 1485, 1486, 1489, 1491, 1492, 1494, 1498, 1505, 1508, 1527, 1528, 1534, 1540, 1542, 1543, 1547, 1561, 1564, 1568, 1569, 1573, 1576, 1585, 1587, 1588, 1601, 1602, 1605, 1607, 1608, 1609, 1611, 1629, 1631, 1635, 1643, 1647, 1657, 1661, 1666, 1667, 1682, 1683, 1690, 1691, 1697, 1705, 1710, 1736, 1750, 1761, 1763, 1765, 1769, 1773, 1785, 1786, 1792, 1796, 1801, 1809, 1812, 1814, 1835, 1844, 1855, 1862, 1863, 1865, 1867, 1872, 1887, 1891, 1892, 1893, 1894, 1910, 1927, 1938, 1941, 1953, 1979, 1982, 1998, 1999, 2000, 2007, 2008, 2009, 2013, 2017, 2019, 2024, 2037, 2044]

idx_test6=[2048, 4, 11, 2060, 13, 2061, 15, 2064, 2067, 2077, 31, 32, 33, 34, 38, 42, 49, 54, 2103, 56, 2106, 66, 67, 2115, 2131, 2132, 2143, 2144, 2149, 2150, 2163, 2166, 2170, 2180, 2184, 2214, 2218, 2222, 2228, 2251, 2254, 2256, 2257, 2259, 2260, 2265, 2278, 2279, 2286, 2306, 2308, 2311, 2313, 2314, 2315, 2318, 2326, 2327, 2332, 2346, 2353, 2366, 2370, 2371, 2372, 2382, 2390, 2394, 2406, 2427, 2445, 2467, 2469, 2470, 2474, 640, 692, 807, 812, 817, 818, 826, 844, 852, 861, 864, 877, 900, 904, 917, 918, 929, 932, 933, 938, 941, 942, 945, 948, 959, 970, 976, 989, 994, 1009, 1018, 1039, 1041, 1042, 1043, 1052, 1053, 1065, 1071, 1080, 1083, 1085, 1106, 1107, 1110, 1111, 1119, 1131, 1132, 1133, 1135, 1149, 1150, 1151, 1157, 1159, 1169, 1170, 1172, 1173, 1176, 1177, 1178, 1179, 1182, 1185, 1187, 1188, 1192, 1193, 1198, 1209, 1210, 1236, 1238, 1242, 1247, 1254, 1255, 1260, 1265, 1267, 1272, 1273, 1280, 1288, 1289, 1290, 1299, 1326, 1327, 1338, 1339, 1340, 1341, 1343, 1344, 1346, 1347, 1348, 1358, 1365, 1366, 1375, 1379, 1394, 1396, 1401, 1403, 1409, 1414, 1420, 1427, 1430, 1440, 1443, 1452, 1454, 1460, 1464, 1467, 1476, 1480, 1482, 1489, 1490, 1493, 1495, 1497, 1499, 1505, 1508, 1510, 1513, 1523, 1532, 1565, 1576, 1578, 1579, 1585, 1586, 1587, 1591, 1592, 1597, 1601, 1602, 1609, 1611, 1629, 1644, 1653, 1663, 1664, 1665, 1667, 1677, 1678, 1684, 1688, 1689, 1709, 1710, 1715, 1717, 1719, 1720, 1728, 1730, 1737, 1739, 1759, 1767, 1773, 1779, 1793, 1797, 1820, 1823, 1824, 1837, 1839, 1853, 1854, 1864, 1865, 1867, 1871, 1877, 1878, 1880, 1882, 1884, 1887, 1894, 1942, 1972, 1983, 1985, 1990, 1993, 1995, 2000, 2001, 2003, 2005, 2007, 2008, 2010, 2018, 2022, 2029, 2036, 2040, 2044, 2045, 2047]
#print("adj.shape[0]",adj.shape[0])
idx_test7=[2048, 13, 2061, 2064, 2077, 32, 34, 54, 66, 2131, 2132, 2170, 2180, 2184, 2214, 2251, 2256, 2259, 2278, 2286, 2346, 2371, 2372, 640, 807, 812, 861, 864, 904, 917, 918, 929, 933, 941, 942, 945, 959, 970, 989, 994, 1041, 1042, 1052, 1065, 1083, 1107, 1110, 1111, 1135, 1150, 1157, 1159, 1170, 1173, 1177, 1185, 1198, 1210, 1236, 1247, 1255, 1265, 1280, 1289, 1290, 1299, 1326, 1327, 1338, 1339, 1341, 1344, 1358, 1379, 1401, 1403, 1414, 1420, 1430, 1443, 1452, 1454, 1464, 1482, 1490, 1495, 1497, 1510, 1513, 1523, 1532, 1578, 1644, 1663, 1664, 1665, 1677, 1688, 1689, 1717, 1720, 1728, 1730, 1737, 1739, 1779, 1797, 1824, 1839, 1853, 1854, 1864, 1887, 1942, 1972, 1985, 2001, 2005, 2010, 2018, 2022, 2036, 2040, 2045, 2047]

#idx_test8=[13, 2064, 2077, 32, 2082, 2131, 2151, 2170, 2184, 2204, 2237, 2244, 2256, 2278, 2286, 2321, 2334, 2346, 2359, 2360, 2365, 2371, 2372, 2392, 2396, 2398, 2399, 640, 812, 869, 870, 917, 925, 929, 930, 931, 933, 939, 942, 943, 944, 953, 959, 970, 983, 1041, 1110, 1150, 1170, 1177, 1185, 1210, 1234, 1236, 1255, 1258, 1281, 1299, 1338, 1351, 1411, 1414, 1420, 1430, 1443, 1454, 1464, 1484, 1495, 1497, 1503, 1509, 1510, 1513, 1523, 1533, 1572, 1578, 1581, 1606, 1622, 1650, 1688, 1689, 1700, 1730, 1731, 1735, 1781, 1788, 1797, 1836, 1864, 1883, 1908, 1976, 2005, 2043, 2045]

idx_test8=[6, 2055, 2057, 10, 2059, 2062, 26, 2075, 2085, 39, 2089, 44, 46, 51, 52, 53, 58, 59, 60, 64, 69, 2117, 2116, 2121, 74, 2124, 77, 2127, 79, 83, 84, 85, 2133, 87, 2138, 92, 96, 94, 99, 2148, 2152, 110, 2159, 112, 116, 118, 2167, 2168, 2169, 124, 2172, 125, 132, 133, 135, 2187, 2188, 142, 141, 2192, 145, 146, 148, 143, 151, 144, 154, 2202, 2205, 157, 2209, 161, 165, 2215, 2216, 171, 172, 174, 2224, 177, 2226, 179, 181, 187, 188, 189, 191, 2241, 196, 199, 200, 203, 2248, 210, 211, 214, 216, 218, 221, 222, 226, 229, 230, 232, 233, 235, 2285, 241, 243, 244, 245, 2294, 247, 251, 2300, 256, 258, 260, 262, 263, 268, 269, 271, 276, 283, 2333, 285, 286, 289, 2338, 2339, 293, 299, 2348, 301, 302, 308, 309, 312, 313, 2369, 325, 328, 329, 2380, 332, 334, 2384, 337, 338, 339, 2386, 343, 344, 2395, 347, 353, 2403, 355, 357, 2408, 362, 369, 371, 2420, 372, 374, 375, 380, 2433, 388, 393, 2444, 398, 2446, 2450, 402, 403, 406, 410, 412, 2462, 418, 420, 423, 424, 2472, 2475, 429, 430, 432, 2482, 2483, 438, 441, 445, 447, 452, 456, 460, 461, 470, 479, 483, 484, 489, 493, 496, 497, 498, 505, 509, 511, 512, 513, 520, 522, 525, 526, 534, 537, 542, 544, 546, 547, 557, 564, 572, 586, 588, 590, 591, 592, 595, 596, 597, 600, 602, 609, 610, 612, 616, 617, 618, 626, 627, 633, 641, 644, 645, 649, 652, 654, 658, 659, 661, 669, 670, 675, 679, 682, 684, 685, 689, 691, 696, 698, 699, 702, 704, 140, 717, 720, 725, 738, 739, 740, 744, 747, 748, 749, 750, 752, 754, 757, 759, 764, 769, 778, 780, 782, 785, 787, 790, 792, 795, 797, 798, 805, 811, 821, 830, 836, 840, 845, 859, 860, 876, 885, 889, 890, 891, 893, 899, 911, 912, 915, 916, 922, 924, 940, 946, 949, 951, 958, 968, 969, 974, 977, 981, 986, 993, 1003, 1004, 1015, 1025, 1027, 1029, 1032, 1057, 1068, 1084, 1092, 1096, 1099, 1100, 1103, 1104, 1109, 1120, 1123, 1134, 1143, 1148, 1152, 1158, 1165, 1186, 1195, 1197, 1201, 1206, 1207, 1212, 1224, 1225, 1229, 1243, 1249, 1262, 1268, 1269, 1283, 1309, 1319, 1362, 1363, 1384, 1388, 1391, 1392, 1397, 1399, 1405, 1406, 1407, 1415, 1417, 1418, 1419, 1438, 1447, 1455, 1459, 1463, 1468, 1471, 1472, 1474, 1491, 1492, 1498, 1502, 1518, 1520, 1535, 1538, 1542, 1543, 1546, 1547, 1550, 1552, 1561, 1569, 1573, 1594, 1603, 1605, 1607, 1614, 1617, 1618, 1621, 1626, 1630, 1631, 1642, 1649, 1662, 1666, 1673, 1679, 1682, 1683, 1692, 1698, 1702, 1705, 1725, 1736, 1740, 1750, 1761, 1763, 1765, 1769, 1770, 1786, 1801, 1805, 1806, 1809, 1830, 1834, 1835, 1840, 1842, 1845, 1863, 1866, 1876, 1881, 1885, 1892, 1893, 1909, 1911, 1919, 1926, 1927, 1929, 1932, 1936, 1944, 1945, 1946, 1953, 1960, 1979, 1984, 1998, 1999, 2004, 2006, 2009, 2011, 2016, 2025, 2026, 2027, 2028, 2032, 2037]

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
#acc [0.8078470824949698, 0.7510060362173039, 0.7374245472837023, 0.7293762575452717]

#neighbor type 1:
#acc [0.7721943048576214, 0.6532663316582915, 0.609715242881072, 0.6046901172529313]

#neighbor type 2:
#acc [0.8131868131868132, 0.7516483516483516, 0.7604395604395604, 0.7582417582417582]

#neighbor type 3:
#acc [0.8240985048372912, 0.7229551451187335, 0.6323658751099385, 0.5989445910290238]

#neighbor type 4:
#acc [0.8450184501845018, 0.8154981549815498, 0.8081180811808117, 0.8081180811808117]

#neighbor type 5:
#acc [0.8413793103448276, 0.7448275862068965, 0.7448275862068965, 0.7333333333333333]

#neighbor type 6:
#acc [0.8430034129692833, 0.8088737201365188, 0.7406143344709898, 0.7542662116040956]

#neighbor type 7:
#acc [0.8240000000000001, 0.808, 0.76, 0.744]

#neighbor type 8:
#acc [0.8484848484848485, 0.7777777777777778, 0.7777777777777778, 0.7676767676767677]

#neighbor type 8-0:
#acc [0.7672064777327935, 0.6659919028340081, 0.5951417004048583, 0.5931174089068826]
