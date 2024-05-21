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
parser.add_argument('--seed', type=int, default=16, help='Random seed.')
parser.add_argument('--epochs', type=int, default=200,
                    help='Number of epochs to train.')
parser.add_argument('--lr', type=float, default=0.01,
                    help='Initial learning rate.')
parser.add_argument('--hidden', type=int, default=16,
                    help='Number of hidden units.')
parser.add_argument('--dataset', type=str, default='citeseer',
                    choices=['cora', 'cora_ml', 'citeseer', 'polblogs'], help='dataset')
parser.add_argument('--ptb_rate', type=float, default=0.05,  help='pertubation rate')
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



idx_test1=[1536, 513, 1540, 5, 519, 2056, 2058, 2059, 1037, 526, 527, 2063, 2065, 2061, 528, 532, 1045, 2071, 2078, 546, 1569, 548, 2082, 1574, 1575, 1578, 554, 45, 2095, 558, 2093, 562, 563, 2101, 2109, 574, 1089, 1602, 1604, 1607, 72, 1609, 1613, 590, 591, 593, 1619, 595, 598, 1634, 1123, 614, 1639, 104, 106, 621, 625, 1663, 1155, 132, 1668, 1673, 1679, 1168, 1687, 1177, 1689, 1692, 158, 1699, 177, 1209, 186, 1728, 1729, 1732, 1221, 199, 200, 709, 1226, 1066, 711, 1742, 1233, 1745, 1746, 1748, 551, 1238, 1242, 731, 1246, 735, 737, 1762, 1252, 233, 235, 1260, 1259, 754, 756, 1783, 1272, 1786, 251, 1789, 247, 1799, 1803, 1293, 1806, 272, 274, 275, 279, 1304, 1815, 1306, 791, 281, 797, 1821, 286, 1310, 1819, 1308, 804, 806, 1316, 1832, 1828, 1831, 1830, 814, 815, 304, 305, 1841, 1849, 314, 1344, 1857, 837, 1862, 1351, 1860, 846, 1359, 1360, 1363, 854, 346, 1371, 354, 1379, 1893, 1897, 363, 364, 1903, 1397, 374, 376, 380, 1917, 898, 901, 1414, 388, 1413, 394, 1421, 400, 913, 1428, 1429, 1430, 404, 409, 410, 411, 1436, 926, 1438, 1953, 1442, 931, 932, 423, 937, 1452, 1965, 1972, 1464, 1466, 1979, 1468, 444, 958, 1475, 1997, 1488, 464, 466, 468, 981, 1494, 474, 987, 1504, 1505, 503, 1509, 486, 1510, 1000, 489, 487, 1004, 493, 2031, 1007, 1521, 501, 502, 506, 1533]

idx_test2=[0, 1, 4, 2053, 6, 8, 2056, 2065, 19, 2070, 23, 2077, 30, 31, 32, 2078, 35, 38, 39, 2087, 2090, 43, 2091, 45, 2093, 48, 2098, 54, 62, 64, 66, 70, 71, 75, 83, 85, 87, 89, 91, 93, 97, 98, 102, 109, 117, 122, 125, 127, 131, 138, 157, 159, 160, 162, 165, 166, 171, 173, 181, 182, 183, 185, 187, 37, 207, 218, 225, 2081, 236, 245, 254, 266, 284, 295, 302, 308, 310, 314, 315, 317, 320, 337, 354, 362, 369, 380, 382, 427, 433, 437, 439, 451, 473, 487, 494, 516, 595, 598, 601, 602, 608, 612, 614, 615, 618, 619, 620, 622, 623, 624, 630, 631, 636, 638, 640, 648, 654, 655, 658, 662, 668, 669, 672, 678, 684, 685, 686, 689, 696, 697, 707, 720, 722, 737, 740, 754, 757, 759, 766, 767, 776, 780, 786, 787, 791, 796, 802, 815, 817, 823, 829, 832, 839, 848, 854, 855, 860, 862, 864, 869, 885, 888, 897, 900, 902, 904, 915, 916, 917, 925, 927, 931, 936, 937, 938, 942, 947, 949, 950, 953, 956, 957, 959, 973, 977, 979, 983, 987, 989, 999, 1001, 1003, 1004, 1019, 1021, 1026, 1027, 1038, 1040, 1049, 1051, 1053, 1054, 1055, 1063, 1070, 1077, 1079, 1083, 1088, 1093, 1105, 1109, 1110, 1119, 1122, 1128, 1131, 1140, 1148, 1150, 1151, 1152, 1154, 1177, 1180, 1189, 1191, 1193, 1194, 1196, 1210, 1220, 1227, 1228, 1232, 1234, 1243, 1246, 1250, 1256, 1263, 1271, 1272, 1273, 1280, 1281, 1283, 1285, 1286, 1287, 1306, 1317, 1324, 1327, 1332, 1333, 1338, 1341, 1345, 1350, 1352, 1355, 1364, 1366, 1379, 1380, 1388, 1390, 1393, 1394, 1400, 1401, 1418, 1425, 1428, 1432, 1433, 1447, 1453, 1454, 1455, 1457, 1462, 1465, 1468, 1483, 1507, 1516, 1519, 1521, 1529, 1530, 1531, 1538, 1547, 1548, 1551, 1553, 1554, 1570, 1572, 1574, 1576, 1584, 1594, 1602, 1604, 1611, 1612, 1617, 1618, 1624, 1625, 1630, 1633, 1635, 1637, 1648, 1653, 1655, 1656, 1659, 1661, 1664, 1665, 1667, 1671, 1675, 1687, 1689, 1694, 1695, 1696, 1706, 1707, 1714, 1716, 1733, 1741, 1750, 1751, 1753, 1763, 1765, 1767, 1771, 1787, 1790, 1793, 1797, 1800, 1803, 1805, 1814, 1816, 1817, 1826, 1829, 1831, 1832, 1833, 1843, 1846, 1848, 1859, 1864, 1877, 1904, 1905, 1910, 1917, 1927, 1930, 1940, 1946, 1952, 1954, 1970, 1978, 2003, 2010, 2019, 2020, 2023, 2029, 2030, 2039, 2043]

idx_test3=[2049, 4, 5, 2055, 2056, 2059, 2061, 14, 13, 17, 2065, 2062, 2069, 2071, 23, 25, 2077, 2080, 2081, 35, 2084, 2085, 2086, 2078, 2089, 2082, 2093, 45, 49, 2098, 2100, 53, 2102, 2101, 56, 57, 2107, 60, 2109, 63, 64, 67, 72, 79, 80, 83, 85, 86, 87, 88, 91, 95, 96, 98, 102, 104, 106, 107, 109, 114, 120, 125, 129, 133, 134, 135, 142, 151, 152, 155, 157, 158, 162, 164, 165, 169, 170, 171, 178, 181, 186, 187, 188, 198, 202, 203, 209, 210, 212, 213, 214, 216, 218, 225, 231, 232, 236, 237, 239, 241, 242, 250, 253, 256, 261, 266, 268, 272, 274, 279, 281, 284, 285, 286, 287, 289, 295, 296, 305, 307, 312, 313, 314, 316, 323, 334, 335, 338, 343, 344, 345, 346, 347, 349, 352, 354, 356, 359, 360, 361, 363, 369, 370, 376, 380, 381, 382, 384, 388, 393, 394, 398, 399, 400, 410, 414, 416, 417, 422, 423, 429, 441, 444, 445, 448, 449, 450, 455, 457, 461, 462, 463, 464, 466, 468, 472, 475, 478, 482, 484, 486, 491, 500, 505, 506, 510, 513, 515, 518, 519, 520, 531, 535, 538, 542, 543, 545, 547, 550, 551, 553, 554, 558, 563, 568, 572, 575, 576, 578, 579, 581, 584, 585, 592, 595, 597, 606, 613, 614, 615, 618, 620, 621, 622, 625, 627, 631, 639, 640, 642, 646, 652, 658, 660, 667, 668, 674, 675, 684, 685, 695, 697, 704, 709, 712, 713, 714, 717, 725, 735, 737, 740, 742, 746, 752, 755, 759, 768, 779, 786, 791, 794, 795, 797, 799, 804, 813, 815, 816, 817, 818, 820, 833, 837, 839, 843, 846, 847, 854, 857, 862, 863, 864, 866, 869, 875, 878, 887, 889, 890, 892, 893, 894, 897, 898, 902, 903, 904, 907, 932, 933, 934, 937, 948, 950, 958, 961, 962, 964, 967, 969, 970, 971, 975, 976, 987, 989, 991, 996, 999, 1000, 1002, 1003, 1006, 1007, 1008, 1019, 1021, 1022, 1026, 1031, 1032, 1037, 1038, 1044, 1049, 1052, 1055, 1056, 1059, 1061, 1063, 1066, 1068, 1071, 1075, 1077, 1086, 1092, 1093, 1095, 1096, 1097, 1100, 1101, 1108, 1110, 1112, 1116, 1121, 1130, 1136, 1137, 1139, 1143, 1146, 1147, 1154, 1155, 1157, 1158, 1161, 1164, 1165, 1166, 1169, 1174, 1175, 1180, 1182, 1183, 1188, 1190, 1191, 1192, 1193, 1194, 1196, 1197, 1198, 1199, 1202, 1208, 1209, 1211, 1212, 1213, 1216, 1221, 1223, 1226, 1227, 1230, 1233, 1238, 1245, 1246, 1247, 1248, 1249, 1250, 1252, 1257, 1260, 1261, 1267, 1271, 1275, 1282, 1293, 1295, 1298, 1301, 1304, 1310, 1312, 1314, 1321, 1322, 1323, 1324, 1332, 1333, 1334, 1335, 1337, 1338, 1339, 1344, 1345, 1346, 1351, 1352, 1353, 1355, 1358, 1363, 1365, 1366, 1370, 1378, 1379, 1381, 1385, 1386, 1389, 1390, 1395, 1400, 1401, 1414, 1417, 1423, 1425, 1428, 1429, 1430, 1431, 1435, 1436, 1437, 1440, 1446, 1447, 1452, 1453, 1455, 1459, 1464, 1465, 1466, 1468, 1469, 1470, 1472, 1475, 1476, 1480, 1481, 1490, 1493, 1494, 1502, 1509, 1511, 1516, 1523, 1534, 1539, 1540, 1542, 1545, 1551, 1552, 1553, 1554, 1565, 1567, 1568, 1569, 1570, 1574, 1578, 1580, 1584, 1596, 1601, 1603, 1604, 1607, 1608, 1609, 1611, 1612, 1613, 1627, 1628, 1629, 1631, 1633, 1634, 1635, 1639, 1641, 1648, 1651, 1663, 1665, 1666, 1668, 1669, 1671, 1673, 1687, 1689, 1692, 1699, 1713, 1715, 1716, 1723, 1724, 1726, 1727, 1732, 1733, 1735, 1739, 1741, 1746, 1751, 1753, 1755, 1757, 1774, 1775, 1781, 1783, 1786, 1787, 1788, 1793, 1799, 1800, 1803, 1805, 1806, 1807, 1811, 1812, 1817, 1821, 1823, 1824, 1830, 1831, 1832, 1833, 1836, 1846, 1848, 1856, 1859, 1860, 1862, 1866, 1873, 1875, 1876, 1885, 1886, 1892, 1893, 1895, 1898, 1903, 1905, 1912, 1916, 1924, 1925, 1928, 1930, 1934, 1935, 1938, 1942, 1946, 1949, 1952, 1953, 1954, 1966, 1972, 1973, 1974, 1980, 1981, 1993, 2000, 2004, 2007, 2009, 2012, 2013, 2015, 2031, 2033, 2034, 2035, 2036, 2040, 2047]

idx_test4=[0, 1027, 3, 5, 2054, 2055, 2052, 11, 2061, 1551, 1553, 23, 537, 1054, 1565, 1564, 2081, 1566, 35, 1572, 1059, 1063, 40, 2090, 43, 2091, 1581, 1077, 1079, 56, 1591, 55, 1594, 62, 65, 1604, 71, 1607, 1608, 1611, 595, 85, 598, 601, 602, 604, 97, 1122, 1635, 611, 614, 618, 1131, 620, 624, 1648, 114, 631, 632, 636, 127, 1665, 1155, 1671, 1164, 652, 1166, 655, 1680, 658, 1180, 157, 668, 1191, 1706, 1708, 684, 688, 1210, 186, 1221, 1227, 207, 1744, 206, 1747, 1750, 733, 737, 740, 228, 236, 749, 245, 759, 760, 1273, 1271, 1791, 1285, 786, 1302, 791, 283, 796, 1313, 1314, 817, 1333, 1334, 1335, 822, 1337, 1338, 1339, 317, 832, 1859, 1364, 854, 1367, 856, 1368, 855, 860, 1885, 862, 868, 869, 363, 1388, 1389, 1390, 1392, 1905, 1394, 885, 1910, 1914, 896, 898, 1415, 905, 1418, 926, 931, 938, 1963, 1453, 1454, 433, 1461, 1462, 1980, 451, 973, 1491, 2012, 1001, 2036, 1019, 1021]

idx_test5=[2055, 2065, 18, 20, 2071, 2077, 2078, 35, 46, 2095, 2098, 2101, 2109, 67, 68, 71, 88, 104, 107, 115, 116, 129, 155, 159, 162, 169, 170, 173, 174, 186, 200, 225, 236, 242, 248, 251, 272, 279, 281, 286, 296, 302, 305, 306, 307, 314, 319, 324, 338, 343, 345, 346, 351, 352, 354, 360, 364, 370, 374, 380, 382, 385, 395, 400, 407, 410, 413, 417, 423, 434, 435, 441, 444, 445, 448, 459, 463, 472, 491, 497, 505, 519, 540, 543, 544, 546, 551, 562, 572, 576, 590, 613, 615, 629, 631, 654, 692, 693, 709, 723, 725, 735, 737, 754, 756, 762, 773, 787, 789, 791, 798, 810, 813, 815, 825, 837, 839, 858, 882, 902, 921, 925, 958, 964, 967, 971, 975, 987, 1003, 1005, 1008, 1046, 1047, 1049, 1061, 1063, 1068, 1081, 1094, 1095, 1100, 1102, 1103, 1108, 1126, 1154, 1157, 1190, 1202, 1209, 1223, 1226, 1227, 1233, 1235, 1246, 1260, 1263, 1264, 1266, 1267, 1275, 1277, 1280, 1304, 1315, 1318, 1321, 1330, 1331, 1345, 1351, 1365, 1370, 1379, 1390, 1414, 1415, 1420, 1423, 1425, 1427, 1428, 1429, 1430, 1438, 1444, 1452, 1464, 1465, 1466, 1468, 1475, 1477, 1480, 1490, 1514, 1523, 1524, 1533, 1536, 1542, 1552, 1570, 1574, 1576, 1596, 1603, 1607, 1608, 1613, 1617, 1619, 1624, 1629, 1630, 1634, 1650, 1652, 1668, 1673, 1682, 1684, 1687, 1692, 1699, 1713, 1716, 1719, 1724, 1727, 1732, 1733, 1735, 1742, 1747, 1751, 1753, 1757, 1767, 1781, 1783, 1786, 1788, 1789, 1797, 1800, 1803, 1806, 1811, 1812, 1817, 1826, 1831, 1832, 1833, 1860, 1862, 1866, 1879, 1891, 1893, 1903, 1934, 1937, 1938, 1952, 1954, 1979, 1990, 1991, 1996, 2001, 2030, 2045, 2046]

idx_test6=[0, 1536, 1026, 1027, 5, 2052, 3, 7, 2053, 2062, 1551, 1553, 21, 23, 1049, 1565, 1054, 1055, 2081, 1570, 35, 32, 1052, 1053, 2087, 1063, 2090, 2091, 40, 560, 50, 1075, 1079, 56, 1083, 62, 66, 1609, 73, 1611, 1612, 1102, 1104, 1105, 595, 85, 597, 601, 602, 604, 608, 1122, 1635, 611, 614, 615, 1643, 620, 109, 622, 1655, 1656, 1143, 122, 1659, 1148, 640, 1665, 1152, 1156, 1671, 648, 1160, 138, 1166, 655, 658, 1684, 662, 665, 1178, 668, 1180, 670, 160, 674, 1191, 1705, 1706, 1196, 684, 688, 1207, 1210, 186, 1220, 1221, 198, 203, 1741, 207, 722, 1750, 1751, 1759, 225, 228, 1767, 1771, 748, 1774, 239, 1262, 1777, 1264, 757, 1271, 760, 759, 1272, 1790, 1791, 1793, 1794, 771, 1285, 1286, 1800, 1294, 784, 786, 1814, 1303, 1816, 794, 288, 289, 1313, 1825, 804, 302, 1327, 1328, 817, 1332, 1333, 1337, 1338, 1339, 1341, 318, 832, 317, 1350, 1352, 1354, 337, 1877, 1366, 1367, 857, 860, 1885, 862, 1886, 863, 1377, 1378, 868, 869, 361, 362, 1388, 1392, 369, 1904, 885, 1910, 886, 1914, 1917, 896, 1409, 897, 1418, 1933, 1940, 1946, 927, 1954, 1445, 423, 936, 938, 1963, 1453, 942, 1454, 1462, 438, 953, 1978, 1979, 1982, 962, 969, 973, 2001, 2003, 989, 2021, 1001, 1519, 1521, 2036, 1013, 1529, 1019, 1021]

idx_test7=[0, 1027, 2052, 3, 7, 2053, 21, 1054, 32, 1053, 2087, 2090, 2091, 40, 560, 50, 1079, 1083, 62, 66, 73, 1102, 1104, 1105, 601, 602, 604, 608, 1122, 611, 1643, 1655, 1656, 122, 1659, 1148, 1152, 1156, 648, 1160, 138, 655, 1684, 662, 665, 1178, 670, 160, 1705, 1706, 688, 1207, 1210, 1220, 207, 722, 1750, 1759, 228, 1767, 1771, 748, 1262, 1777, 1264, 757, 760, 1790, 1791, 1794, 771, 1285, 1286, 1294, 784, 1814, 1303, 1816, 288, 1313, 1825, 302, 1327, 1328, 1341, 318, 832, 317, 1350, 1354, 337, 1877, 1367, 860, 1377, 868, 362, 1388, 1392, 1904, 885, 1910, 886, 1914, 896, 1409, 1418, 1933, 1940, 927, 1445, 936, 938, 1963, 942, 1454, 1462, 438, 953, 1978, 1982, 973, 2001, 2003, 2021, 1001, 1519, 1013, 1529]
#print("adj.shape[0]",adj.shape[0])
#idx_test8=[0, 1027, 3, 2054, 2052, 11, 537, 1054, 1564, 1566, 1572, 40, 2090, 43, 2091, 1581, 1079, 1591, 55, 1594, 62, 65, 71, 601, 602, 604, 97, 1122, 611, 1131, 624, 632, 636, 127, 655, 1680, 1706, 1708, 688, 1210, 207, 1744, 206, 1747, 1750, 733, 228, 749, 245, 760, 1273, 1791, 1285, 1302, 283, 796, 1313, 822, 317, 832, 1364, 1367, 856, 1368, 855, 860, 868, 1388, 1392, 1394, 885, 1910, 1914, 896, 1415, 905, 1418, 938, 1963, 1454, 433, 1461, 1462, 451, 973, 1491, 1001]

idx_test8=[513, 1540, 519, 2056, 2058, 2059, 1037, 526, 527, 2063, 2065, 528, 532, 1045, 2071, 2078, 546, 1569, 548, 2082, 1574, 1575, 1578, 554, 45, 2095, 558, 2093, 562, 563, 2101, 2109, 574, 1089, 1602, 72, 1613, 590, 591, 593, 1619, 1634, 1123, 1639, 104, 106, 621, 625, 1663, 132, 1668, 1673, 1679, 1168, 1687, 1177, 1689, 1692, 158, 1699, 177, 1209, 1728, 1729, 1732, 199, 200, 709, 1226, 1066, 711, 1742, 1233, 1745, 1746, 1748, 551, 1238, 1242, 731, 1246, 735, 1762, 1252, 233, 235, 1260, 1259, 754, 756, 1783, 1786, 251, 1789, 247, 1799, 1803, 1293, 1806, 272, 274, 275, 279, 1304, 1815, 1306, 281, 797, 1821, 286, 1310, 1819, 1308, 806, 1316, 1832, 1828, 1831, 1830, 814, 815, 304, 305, 1841, 1849, 314, 1344, 1857, 837, 1862, 1351, 1860, 846, 1359, 1360, 1363, 346, 1371, 354, 1379, 1893, 1897, 364, 1903, 1397, 374, 376, 380, 901, 1414, 388, 1413, 394, 1421, 400, 913, 1428, 1429, 1430, 404, 409, 410, 411, 1436, 1438, 1953, 1442, 932, 937, 1452, 1965, 1972, 1464, 1466, 1468, 444, 958, 1475, 1997, 1488, 464, 466, 468, 981, 1494, 474, 987, 1504, 1505, 503, 1509, 486, 1510, 1000, 489, 487, 1004, 493, 2031, 1007, 501, 502, 506, 1533]

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
#acc [0.6954976303317536, 0.6125592417061612, 0.5071090047393365, 0.4431279620853081]
#acc [0.6954976303317536, 0.6255924170616114, 0.5290284360189574, 0.4940758293838863]

#neighbor type 1:
# acc [0.7117903930131004, 0.5065502183406113,0.42358078602620086,0.4279475982532751]
#acc [0.7117903930131004, 0.5764192139737991, 0.4803493449781659, 0.4890829694323144]

#neighbor type 2:
# acc [0.6863753213367608, 0.6066838046272494, 0.5938303341902313, 0.5989717223650385]
#acc [0.6863753213367608, 0.6735218508997429, 0.6940874035989717, 0.6889460154241644]

#neighbor type 3:
#acc [0.7713841368584758, 0.5940902021772939, 0.5956454121306376, 0.6127527216174183]
#acc [0.7713841368584758, 0.656298600311042, 0.5334370139968896, 0.5225505443234837]
    
#neighbor type 4:
#acc [0.6604938271604938, 0.6419753086419753, 0.654320987654321, 0.6419753086419753]
#acc [0.6604938271604938, 0.654320987654321, 0.6234567901234568, 0.6172839506172839]

#neighbor type 5:
#acc [0.7862318840579711, 0.6630434782608696,  0.5543478260869565, 0.5036231884057971]
#acc [0.7862318840579711, 0.6702898550724637, 0.6594202898550725, 0.6521739130434783]

#neighbor type 6:
#acc [0.730593607305936, 0.726027397260274, 0.6621004566210045, 0.6940639269406392]
#acc [0.730593607305936, 0.730593607305936, 0.6986301369863013, 0.6757990867579908]

#neighbor type 7:
#acc [0.689922480620155, 0.689922480620155, 0.6511627906976745, 0.6511627906976745]

#neighbor type 8:
#acc [0.6091954022988506, 0.6666666666666666, 0.6206896551724138, 0.5977011494252873]

#neighbor type 8-0:
#acc [0.7303921568627451, 0.5147058823529411, 0.4411764705882353, 0.4215686274509804]
#acc [0.7303921568627451, 0.553921568627451, 0.5784313725490196, 0.553921568627451]