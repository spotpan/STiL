import torch
#from hitsgnn import HITSGNN
#from hitsgnn_rev2 import HITSGNN
from hitsgnn_rev2_chameleon import HITSGNN_ADAPTIVE

#from hitsgnn_chameleon import HITSGNN_ADAPTIVE

#from hits_prgnn_chameleon import HITSGNN_ADAPTIVE

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
parser.add_argument('--seed', type=int, default=15, help='Random seed.')
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
    hitsgnn = HITSGNN_ADAPTIVE(nfeat=features.shape[1],
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
 
    modified_adj = model(features, adj, labels, idx_train,
                         idx_unlabeled, perturbations, ll_constraint=False)
    modified_adj = modified_adj.detach()


    tensor = modified_adj - adj

    nonzero_indices = torch.nonzero(tensor)

    nonzero_tuples = [(index[0].item(), index[1].item()) for index in nonzero_indices]
    
    print("nonzero_tuples", len(nonzero_tuples))

    print(nonzero_tuples)


    idx_test1=[2064, 2067, 2068, 2075, 2078, 34, 2084, 2085, 2093, 2101, 2104, 2107, 67, 68, 80, 86, 96, 134, 136, 139, 140, 144, 146, 149, 158, 181, 186, 192, 203, 220, 225, 231, 237, 241, 242, 248, 256, 258, 261, 268, 271, 272, 274, 275, 280, 286, 300, 305, 312, 348, 350, 354, 356, 359, 364, 370, 379, 380, 388, 391, 392, 394, 403, 414, 424, 426, 431, 436, 444, 445, 450, 459, 464, 472, 478, 481, 486, 489, 496, 497, 502, 507, 509, 513, 515, 519, 524, 528, 530, 534, 536, 552, 567, 572, 579, 584, 588, 595, 606, 614, 628, 635, 640, 646, 650, 663, 668, 676, 693, 711, 726, 731, 735, 737, 754, 797, 804, 805, 806, 808, 815, 819, 837, 843, 845, 854, 870, 873, 879, 923, 928, 929, 948, 950, 967, 984, 989, 999, 1007, 1056, 1057, 1067, 1074, 1089, 1098, 1135, 1156, 1163, 1179, 1180, 1194, 1195, 1202, 1206, 1237, 1242, 1246, 1261, 1263, 1280, 1295, 1299, 1301, 1316, 1318, 1319, 1322, 1325, 1337, 1338, 1339, 1349, 1352, 1355, 1368, 1370, 1385, 1397, 1400, 1407, 1412, 1426, 1429, 1446, 1450, 1452, 1475, 1481, 1490, 1493, 1494, 1509, 1511, 1550, 1552, 1563, 1590, 1607, 1609, 1629, 1633, 1634, 1645, 1647, 1663, 1668, 1670, 1693, 1699, 1711, 1715, 1716, 1717, 1732, 1733, 1738, 1740, 1745, 1746, 1757, 1768, 1788, 1797, 1799, 1800, 1806, 1817, 1831, 1832, 1846, 1848, 1859, 1860, 1861, 1867, 1871, 1879, 1893, 1909, 1917, 1922, 1928, 1930, 1947, 1953, 1959, 1962, 1964, 1988, 1994, 2011, 2015, 2036, 2044]

    idx_test2=[0, 1, 5, 6, 2055, 8, 2056, 19, 2068, 21, 2070, 2073, 2075, 2078, 33, 34, 2084, 2080, 39, 2081, 36, 2090, 2091, 2087, 45, 47, 51, 2099, 54, 2105, 63, 64, 75, 78, 80, 83, 84, 85, 86, 87, 89, 91, 92, 93, 94, 98, 102, 109, 114, 125, 138, 139, 28, 144, 147, 148, 157, 160, 162, 166, 167, 176, 35, 181, 200, 204, 207, 218, 220, 226, 227, 262, 263, 278, 293, 297, 317, 318, 321, 354, 361, 362, 380, 390, 392, 401, 430, 433, 439, 447, 487, 498, 516, 524, 537, 560, 595, 598, 601, 602, 607, 609, 612, 613, 614, 616, 619, 620, 622, 623, 624, 628, 630, 638, 640, 645, 649, 653, 654, 655, 657, 660, 662, 668, 678, 684, 685, 686, 688, 697, 704, 707, 718, 720, 721, 725, 736, 737, 751, 759, 760, 764, 783, 784, 796, 802, 815, 817, 825, 829, 830, 831, 832, 850, 854, 857, 858, 860, 862, 864, 868, 869, 870, 871, 872, 885, 896, 903, 904, 908, 914, 917, 922, 924, 936, 938, 944, 945, 948, 950, 953, 956, 957, 959, 973, 974, 979, 982, 983, 988, 999, 1002, 1003, 1007, 1009, 1012, 1013, 1019, 1021, 1026, 1027, 1029, 1030, 1038, 1042, 1043, 1048, 1049, 1051, 1054, 1059, 1063, 1069, 1074, 1075, 1078, 1079, 1082, 1090, 1093, 1099, 1109, 1110, 1118, 1119, 1127, 1144, 1149, 1155, 1156, 1159, 1160, 1171, 1173, 1178, 1180, 1183, 1185, 1193, 1194, 1196, 1206, 1210, 1221, 1225, 1234, 1236, 1250, 1279, 1280, 1283, 1289, 1298, 1299, 1301, 1311, 1324, 1327, 1333, 1337, 1338, 1339, 1341, 1348, 1355, 1356, 1367, 1368, 1378, 1381, 1388, 1393, 1400, 1401, 1403, 1409, 1418, 1428, 1433, 1449, 1455, 1456, 1462, 1468, 1476, 1481, 1493, 1515, 1530, 1534, 1536, 1537, 1538, 1543, 1550, 1551, 1553, 1554, 1570, 1572, 1576, 1591, 1599, 1604, 1622, 1635, 1643, 1644, 1648, 1649, 1653, 1658, 1665, 1667, 1672, 1677, 1687, 1694, 1695, 1706, 1707, 1710, 1714, 1716, 1733, 1741, 1750, 1751, 1770, 1784, 1795, 1800, 1801, 1803, 1805, 1813, 1814, 1816, 1817, 1829, 1843, 1846, 1855, 1859, 1863, 1864, 1887, 1904, 1905, 1917, 1930, 1940, 1943, 1946, 1948, 1952, 1958, 1963, 1969, 1978, 1986, 1988, 2005, 2015, 2019, 2020, 2026, 2043]

    idx_test3=[2049, 5, 2055, 2056, 13, 2061, 17, 2066, 2068, 25, 2073, 2078, 2080, 2081, 34, 2084, 2085, 2089, 2093, 46, 2095, 2096, 49, 2098, 2100, 53, 2101, 2102, 57, 59, 63, 64, 67, 68, 72, 78, 79, 80, 83, 85, 86, 87, 91, 96, 97, 98, 102, 103, 104, 106, 107, 109, 111, 113, 114, 115, 120, 121, 125, 136, 139, 144, 145, 146, 152, 157, 158, 162, 164, 173, 176, 178, 181, 186, 188, 192, 194, 195, 196, 200, 202, 203, 212, 214, 215, 216, 218, 222, 225, 228, 232, 237, 240, 241, 242, 243, 247, 248, 250, 256, 261, 268, 269, 272, 277, 285, 290, 294, 313, 316, 328, 329, 338, 343, 344, 345, 346, 348, 349, 354, 359, 361, 369, 370, 371, 375, 376, 378, 379, 381, 384, 388, 389, 394, 398, 399, 403, 405, 407, 408, 414, 415, 416, 417, 419, 420, 423, 424, 425, 429, 432, 434, 441, 442, 444, 445, 447, 450, 455, 456, 457, 459, 461, 465, 472, 475, 478, 484, 486, 487, 491, 497, 499, 500, 503, 506, 507, 513, 517, 518, 519, 523, 524, 525, 529, 531, 532, 534, 535, 538, 540, 542, 544, 547, 548, 551, 553, 554, 555, 556, 559, 563, 568, 572, 576, 578, 585, 590, 592, 595, 597, 606, 613, 614, 620, 622, 627, 628, 634, 635, 638, 640, 641, 642, 645, 646, 649, 650, 660, 661, 668, 670, 684, 685, 690, 692, 693, 695, 704, 705, 709, 710, 712, 716, 718, 719, 731, 734, 735, 739, 741, 742, 746, 754, 755, 756, 758, 759, 764, 776, 778, 781, 785, 791, 792, 793, 797, 799, 802, 804, 805, 808, 809, 817, 819, 820, 821, 825, 837, 839, 845, 850, 854, 862, 863, 864, 865, 870, 878, 881, 884, 887, 889, 893, 894, 903, 904, 909, 911, 912, 916, 920, 934, 939, 948, 950, 956, 959, 962, 967, 974, 975, 976, 980, 982, 986, 989, 999, 1000, 1003, 1006, 1008, 1018, 1019, 1021, 1022, 1026, 1028, 1032, 1035, 1036, 1037, 1038, 1044, 1045, 1046, 1048, 1049, 1055, 1056, 1057, 1058, 1059, 1061, 1062, 1063, 1066, 1067, 1069, 1074, 1075, 1076, 1077, 1085, 1086, 1089, 1091, 1092, 1093, 1094, 1096, 1097, 1100, 1101, 1111, 1112, 1118, 1123, 1127, 1132, 1135, 1138, 1142, 1143, 1144, 1145, 1155, 1162, 1163, 1164, 1165, 1168, 1170, 1180, 1187, 1192, 1193, 1194, 1195, 1196, 1198, 1199, 1202, 1206, 1209, 1213, 1221, 1226, 1230, 1233, 1238, 1241, 1242, 1246, 1247, 1249, 1252, 1256, 1257, 1259, 1260, 1261, 1263, 1271, 1288, 1289, 1290, 1293, 1295, 1298, 1299, 1300, 1301, 1306, 1312, 1318, 1319, 1320, 1321, 1322, 1325, 1326, 1333, 1334, 1335, 1337, 1338, 1339, 1342, 1343, 1345, 1346, 1351, 1352, 1353, 1355, 1361, 1363, 1365, 1368, 1370, 1380, 1383, 1385, 1386, 1389, 1395, 1397, 1399, 1400, 1401, 1417, 1423, 1426, 1428, 1429, 1435, 1438, 1440, 1442, 1446, 1452, 1455, 1456, 1462, 1464, 1465, 1466, 1468, 1472, 1475, 1476, 1481, 1489, 1490, 1492, 1494, 1496, 1498, 1499, 1504, 1509, 1515, 1516, 1526, 1529, 1534, 1540, 1542, 1544, 1545, 1551, 1552, 1553, 1554, 1556, 1558, 1559, 1568, 1569, 1570, 1571, 1580, 1589, 1590, 1592, 1603, 1604, 1607, 1608, 1609, 1611, 1612, 1614, 1617, 1619, 1629, 1633, 1634, 1635, 1638, 1647, 1648, 1651, 1653, 1662, 1663, 1665, 1666, 1668, 1670, 1671, 1673, 1674, 1679, 1680, 1685, 1687, 1689, 1699, 1702, 1712, 1713, 1715, 1716, 1723, 1724, 1725, 1726, 1728, 1729, 1732, 1733, 1736, 1739, 1740, 1741, 1743, 1746, 1751, 1756, 1757, 1759, 1760, 1761, 1776, 1781, 1788, 1792, 1799, 1800, 1802, 1803, 1804, 1805, 1806, 1812, 1817, 1819, 1824, 1826, 1830, 1831, 1832, 1842, 1848, 1853, 1856, 1857, 1859, 1860, 1866, 1867, 1870, 1873, 1879, 1892, 1893, 1898, 1899, 1907, 1917, 1918, 1928, 1930, 1934, 1935, 1941, 1945, 1946, 1949, 1952, 1953, 1956, 1973, 1974, 1977, 1980, 1981, 1985, 1986, 1988, 1989, 1993, 2001, 2004, 2012, 2015, 2018, 2031, 2033, 2034, 2035, 2038, 2041, 2045, 2046]

    idx_test4=[0, 1026, 1027, 1018, 6, 2055, 1544, 1019, 10, 1547, 12, 13, 1038, 1036, 1553, 1554, 537, 30, 1054, 1569, 1059, 2084, 1572, 36, 39, 1063, 2085, 2090, 37, 2091, 1069, 1581, 2098, 1078, 1079, 54, 60, 63, 1603, 1604, 1607, 1608, 75, 76, 78, 79, 595, 85, 598, 601, 602, 89, 607, 97, 1635, 1636, 614, 1127, 102, 619, 623, 114, 1144, 632, 1659, 636, 637, 1150, 1151, 1665, 1155, 644, 645, 1159, 1160, 655, 1680, 659, 660, 147, 1687, 155, 156, 1180, 1694, 157, 160, 678, 677, 1706, 1196, 688, 1200, 1721, 1210, 187, 718, 207, 1232, 209, 1750, 1752, 218, 220, 736, 227, 740, 1767, 1770, 1791, 1283, 1284, 1286, 1288, 1289, 778, 793, 796, 1311, 800, 1825, 802, 1827, 809, 1839, 817, 1333, 1334, 1335, 823, 826, 1341, 831, 832, 1345, 1859, 1348, 838, 1350, 1863, 1872, 854, 1368, 862, 1887, 362, 363, 1388, 1389, 1392, 1905, 1394, 1904, 1397, 1910, 1911, 885, 380, 1917, 896, 898, 904, 905, 1418, 908, 914, 1428, 1945, 926, 1952, 931, 938, 1451, 430, 1455, 943, 433, 1461, 1978, 1980, 956, 1982, 447, 1983, 960, 1989, 1481, 1491, 1496, 2020, 1513, 1517, 1010, 2038, 2042, 1531, 1021]

    idx_test5=[5, 2071, 2076, 2078, 2084, 2085, 45, 2101, 2104, 2105, 2107, 64, 67, 79, 83, 85, 86, 87, 91, 149, 155, 162, 164, 168, 172, 178, 180, 186, 193, 195, 202, 208, 218, 221, 225, 231, 237, 241, 242, 246, 258, 259, 268, 274, 275, 277, 278, 290, 300, 305, 313, 316, 328, 329, 330, 338, 342, 343, 344, 345, 350, 354, 367, 371, 376, 380, 381, 392, 401, 403, 405, 422, 424, 447, 459, 460, 475, 478, 486, 490, 497, 503, 507, 509, 517, 519, 524, 535, 536, 542, 547, 551, 556, 563, 567, 572, 590, 595, 605, 614, 620, 622, 628, 635, 640, 641, 645, 650, 660, 663, 685, 705, 709, 721, 735, 736, 737, 738, 759, 779, 781, 809, 837, 857, 869, 870, 871, 894, 903, 904, 923, 924, 928, 932, 948, 950, 959, 967, 974, 975, 978, 980, 1003, 1007, 1008, 1018, 1041, 1044, 1056, 1059, 1061, 1062, 1063, 1074, 1075, 1076, 1082, 1089, 1098, 1099, 1100, 1110, 1118, 1126, 1132, 1155, 1163, 1164, 1168, 1177, 1179, 1180, 1187, 1193, 1194, 1196, 1198, 1202, 1204, 1226, 1238, 1241, 1260, 1261, 1295, 1299, 1301, 1313, 1320, 1322, 1329, 1336, 1337, 1338, 1339, 1344, 1361, 1363, 1385, 1400, 1405, 1409, 1427, 1428, 1429, 1435, 1438, 1440, 1451, 1452, 1455, 1456, 1470, 1475, 1481, 1492, 1493, 1499, 1543, 1565, 1566, 1568, 1571, 1576, 1586, 1590, 1603, 1607, 1608, 1614, 1621, 1629, 1631, 1635, 1653, 1654, 1663, 1668, 1671, 1685, 1694, 1699, 1701, 1725, 1732, 1733, 1756, 1759, 1784, 1788, 1797, 1800, 1806, 1809, 1846, 1870, 1871, 1880, 1881, 1892, 1893, 1902, 1907, 1916, 1941, 1947, 1952, 1953, 1988, 2004, 2040, 2044, 2045]

    idx_test6=[0, 1, 1026, 1027, 5, 6, 2055, 2053, 521, 516, 1035, 1036, 1541, 1038, 1553, 1554, 1550, 21, 1558, 1551, 537, 1049, 2076, 1055, 2080, 34, 1059, 2081, 1063, 42, 2090, 1069, 1582, 47, 1072, 1586, 1587, 54, 1079, 1591, 1598, 65, 1603, 1604, 1605, 1601, 1609, 80, 595, 83, 85, 598, 87, 89, 602, 1631, 97, 1121, 1635, 1124, 613, 614, 1127, 104, 619, 620, 109, 622, 623, 1648, 113, 1649, 1138, 114, 1140, 1141, 122, 1151, 1665, 1154, 1156, 645, 1159, 1161, 141, 655, 1680, 657, 144, 1171, 660, 148, 662, 656, 666, 155, 668, 669, 1183, 160, 1180, 679, 167, 681, 1194, 1193, 1196, 684, 688, 1201, 689, 1207, 1210, 704, 707, 1220, 1229, 1231, 207, 1234, 722, 1750, 1751, 223, 737, 227, 230, 745, 1258, 759, 1273, 1791, 1795, 1283, 771, 1286, 1284, 1288, 1289, 1800, 1295, 783, 1813, 792, 796, 1822, 1311, 1313, 802, 1826, 1827, 1829, 808, 809, 1324, 1838, 1327, 1840, 817, 1842, 1843, 1329, 1333, 1334, 1335, 317, 1855, 320, 832, 1858, 1859, 1348, 835, 1350, 1355, 1869, 1872, 1877, 1368, 860, 862, 354, 1381, 869, 1388, 1903, 369, 1397, 885, 887, 888, 1403, 1927, 904, 905, 906, 1419, 914, 1428, 916, 1432, 921, 412, 415, 927, 936, 425, 938, 1450, 953, 1980, 1468, 1982, 447, 957, 1473, 1476, 1990, 1481, 1488, 1497, 2012, 2015, 2020, 1509, 999, 2023, 1003, 1517, 1010, 501, 2038, 1021]


    idx_test7=[ ele for ele in idx_test if ele not in idx_test1 and ele not in idx_test2 
               and ele not in idx_test3 and ele not in idx_test4 
               and ele not in idx_test5 and ele not in idx_test6 ]
    #idx_test7=[ ele for ele in idx_val if ele in idx_test7]

    # Extract unique elements from tuples
    unique_elements = set([elem for tup in nonzero_tuples for elem in tup])

    print("unique_elements", len(unique_elements))

    # Count occurrences of unique elements in test lists
    count_list1 = sum(1 for elem in unique_elements if elem in idx_test1)
    count_list2 = sum(1 for elem in unique_elements if elem in idx_test2)
    count_list3 = sum(1 for elem in unique_elements if elem in idx_test3)
    count_list4 = sum(1 for elem in unique_elements if elem in idx_test4)
    count_list5 = sum(1 for elem in unique_elements if elem in idx_test5)
    count_list6 = sum(1 for elem in unique_elements if elem in idx_test6)
    count_list7 = sum(1 for elem in unique_elements if elem in idx_test7)

    print("Unique Elements:", unique_elements)
    print("Count in list1:", count_list1)
    print("Count in list2:", count_list2)
    print("Count in list3:", count_list3)
    print("Count in list4:", count_list4)
    print("Count in list5:", count_list5)
    print("Count in list6:", count_list6)
    print("Count in list7:", count_list7)

    bar=[count_list1, count_list2, count_list3, count_list4, count_list5, count_list6, count_list7]

    percentage = [ele/sum(bar) * 100 for ele in bar]
        
    print("percentage", percentage)

    # Plot the counts as a bar chart
    plt.bar([1, 2, 3, 4 ,5, 6, 7], 
            [count_list1, count_list2, count_list3, count_list4, 
             count_list5, count_list6, count_list7], 
            tick_label=['n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n<not1&2hop>'])
    plt.xlabel('Test Distribution')
    plt.ylabel('Counts')
    plt.title('Counts of Trapped Edges')
    plt.show()

    #runs = 10
    #clean_acc = []
    #attacked_acc = []
    #print('=== testing HITSGNN on original(clean) graph ===')
    #for i in range(runs):
    #    clean_acc.append(test(adj))

    #print("clean_acc:",clean_acc)

    #print('=== testing HITSGNN on attacked graph ===')
    #for i in range(runs):
    #    attacked_acc.append(test(modified_adj))


    #data=pd.DataFrame({"Acc. Clean":clean_acc,"Acc. Perturbed":attacked_acc})

    #plt.figure(figsize=(6,6))
    #sns.boxplot(data=data)#, re_trainings*[accuracy_logistic]])

    #plt.title("Accuracy before/after perturbing {}% edges using model {}".format(args.ptb_rate*100, args.model))
    #plt.savefig("results_on_{}.png".format(args.dataset), dpi=600)
    #plt.show()


if __name__ == '__main__':
    main()

