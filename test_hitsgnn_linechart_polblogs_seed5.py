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
parser.add_argument('--dataset', type=str, default='polblogs',
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


idx_test1=[0, 1, 2, 4, 5, 11, 13, 15, 16, 18, 19, 20, 21, 23, 25, 28, 29, 30, 31, 33, 34, 35, 36, 41, 42, 43, 44, 45, 46, 47, 50, 51, 52, 53, 68, 72, 73, 74, 80, 81, 84, 85, 86, 91, 92, 94, 95, 96, 99, 100, 103, 105, 110, 111, 112, 114, 116, 117, 118, 119, 125, 126, 127, 130, 132, 134, 140, 146, 147, 149, 151, 153, 154, 155, 156, 158, 160, 162, 164, 165, 168, 169, 172, 178, 181, 183, 186, 191, 194, 196, 197, 199, 200, 204, 206, 211, 213, 216, 218, 219, 220, 221, 224, 225, 227, 228, 230, 232, 234, 235, 236, 237, 239, 242, 243, 244, 246, 248, 250, 254, 259, 262, 265, 267, 270, 271, 273, 278, 280, 282, 285, 290, 291, 294, 300, 304, 306, 308, 310, 312, 313, 316, 320, 322, 324, 329, 333, 334, 337, 338, 339, 340, 342, 343, 344, 345, 347, 348, 350, 352, 355, 357, 358, 359, 361, 363, 364, 365, 368, 370, 371, 372, 374, 378, 379, 382, 383, 384, 385, 387, 388, 390, 391, 393, 395, 398, 401, 402, 403, 411, 413, 414, 417, 418, 420, 421, 423, 424, 426, 427, 428, 429, 430, 431, 435, 436, 437, 438, 439, 440, 443, 444, 445, 446, 447, 448, 449, 451, 452, 458, 459, 461, 463, 465, 466, 468, 471, 473, 474, 477, 480, 483, 484, 485, 487, 491, 492, 494, 495, 496, 497, 499, 500, 502, 503, 504, 505, 506, 510, 513, 514, 515, 516, 517, 521, 522, 523, 524, 525, 526, 527, 531, 533, 534, 535, 542, 543, 545, 546, 552, 554, 558, 562, 563, 564, 566, 569, 575, 576, 577, 579, 581, 582, 583, 590, 591, 592, 593, 594, 596, 597, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 613, 614, 616, 618, 619, 620, 621, 622, 623, 627, 629, 630, 632, 634, 635, 636, 637, 642, 644, 645, 646, 648, 649, 650, 651, 653, 654, 656, 657, 658, 659, 660, 661, 662, 664, 665, 666, 668, 669, 670, 671, 672, 674, 675, 678, 681, 683, 685, 686, 687, 688, 691, 692, 694, 695, 698, 700, 704, 705, 706, 708, 710, 711, 712, 714, 715, 717, 718, 719, 721, 723, 724, 725, 727, 728, 731, 733, 734, 735, 736, 738, 740, 741, 742, 743, 744, 745, 746, 747, 749, 752, 754, 755, 759, 761, 762, 763, 764, 765, 767, 768, 771, 772, 775, 776, 777, 780, 782, 783, 784, 785, 787, 788, 789, 790, 792, 795, 798, 799, 802, 803, 804, 805, 806, 807, 808, 810, 811, 813, 815, 817, 819, 820, 821, 823, 824, 825, 826, 827, 828, 829, 830, 831, 836, 839, 840, 844, 845, 846, 847, 848, 850, 851, 852, 853, 854, 855, 858, 859, 862, 863, 864, 867, 868, 869, 870, 873, 874, 875, 876, 878, 880, 881, 882, 883, 884, 885, 887, 888, 889, 891, 893, 897, 898, 899, 900, 901, 903, 904, 907, 908, 909, 910, 911, 913, 914, 915, 916, 917, 918, 919, 921, 922, 924, 925, 926, 927, 928, 929, 932, 933, 934, 935, 937, 938, 940, 941, 944, 949, 950, 955, 956, 957, 960, 961, 962, 963, 965, 967, 970, 972, 974, 975, 976, 978, 979, 980, 982, 986, 987, 988, 989, 990, 991, 992, 993, 996, 998, 1000, 1002, 1004, 1005, 1006, 1008, 1009, 1010, 1012, 1013, 1014, 1015, 1017, 1023, 1024, 1025, 1028, 1030, 1032, 1033, 1036, 1039, 1042, 1045, 1048, 1049, 1051, 1052, 1056, 1057, 1058, 1062, 1065, 1067, 1068, 1070, 1071, 1073, 1074, 1076, 1077, 1078, 1079, 1080, 1082, 1084, 1085, 1086, 1087, 1088, 1091, 1092, 1093, 1095, 1096, 1097, 1098, 1099, 1100, 1103, 1104, 1106, 1112, 1113, 1116, 1118, 1120, 1121, 1122, 1123, 1126, 1127, 1131, 1132, 1133, 1135, 1136, 1138, 1141, 1142, 1143, 1145, 1147, 1149, 1150, 1154, 1156, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1170, 1172, 1173, 1175, 1176, 1181, 1182, 1183, 1185, 1186, 1187, 1188, 1191, 1192, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1202, 1203, 1205, 1207, 1208, 1209, 1210, 1211, 1212, 1214, 1216, 1217, 1218, 1220]

idx_test2=[0, 1, 2, 3, 5, 6, 8, 9, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 28, 29, 30, 31, 32, 34, 36, 39, 41, 42, 43, 46, 47, 48, 49, 52, 53, 56, 57, 58, 63, 66, 68, 70, 73, 77, 78, 81, 82, 84, 85, 86, 87, 92, 93, 94, 95, 96, 97, 99, 100, 101, 102, 103, 104, 107, 109, 111, 112, 114, 115, 116, 117, 118, 120, 121, 123, 124, 126, 127, 128, 130, 131, 132, 134, 135, 140, 142, 143, 144, 145, 146, 147, 148, 149, 151, 152, 153, 154, 155, 156, 158, 159, 161, 162, 164, 165, 166, 168, 169, 170, 171, 175, 177, 178, 179, 181, 182, 183, 190, 191, 192, 193, 197, 198, 200, 203, 204, 205, 206, 207, 211, 212, 213, 215, 216, 217, 218, 219, 220, 221, 222, 224, 225, 229, 230, 231, 232, 233, 234, 235, 236, 237, 239, 240, 241, 242, 243, 244, 245, 247, 248, 251, 253, 254, 255, 256, 259, 260, 262, 264, 265, 266, 267, 270, 271, 272, 273, 275, 276, 277, 278, 280, 281, 282, 284, 286, 289, 290, 291, 294, 295, 296, 297, 298, 299, 300, 301, 303, 304, 306, 308, 310, 313, 314, 316, 320, 323, 324, 325, 327, 328, 329, 330, 331, 333, 334, 335, 337, 338, 339, 340, 341, 342, 343, 344, 345, 348, 350, 351, 352, 354, 355, 357, 358, 359, 361, 363, 364, 365, 366, 368, 369, 370, 371, 372, 374, 379, 381, 382, 383, 384, 385, 386, 388, 389, 390, 391, 392, 393, 395, 396, 398, 399, 400, 401, 404, 405, 407, 409, 411, 413, 416, 417, 418, 419, 420, 421, 422, 423, 426, 427, 429, 430, 431, 435, 436, 437, 438, 439, 440, 443, 444, 445, 446, 447, 448, 449, 451, 452, 453, 454, 458, 459, 461, 463, 464, 465, 466, 467, 468, 471, 473, 474, 475, 476, 477, 478, 479, 480, 484, 485, 486, 487, 488, 489, 492, 493, 494, 495, 496, 497, 499, 500, 501, 502, 503, 504, 505, 511, 513, 514, 515, 516, 517, 518, 521, 522, 523, 524, 525, 526, 527, 528, 530, 531, 532, 534, 535, 538, 540, 541, 542, 544, 545, 546, 547, 548, 550, 551, 552, 554, 556, 561, 562, 563, 564, 566, 567, 568, 569, 573, 574, 575, 576, 577, 579, 580, 581, 582, 583, 584, 587, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 605, 606, 607, 608, 609, 610, 611, 613, 614, 616, 617, 621, 622, 623, 624, 627, 628, 629, 630, 631, 632, 634, 635, 636, 637, 642, 644, 646, 647, 648, 649, 650, 651, 654, 656, 657, 658, 659, 660, 661, 662, 664, 667, 668, 669, 670, 671, 672, 673, 674, 675, 677, 678, 680, 681, 684, 687, 688, 689, 690, 691, 692, 694, 695, 697, 698, 699, 700, 703, 704, 705, 706, 708, 710, 712, 714, 715, 717, 718, 719, 721, 722, 724, 725, 727, 728, 729, 730, 731, 733, 734, 736, 737, 738, 740, 741, 742, 743, 744, 746, 747, 749, 752, 753, 755, 756, 761, 762, 763, 764, 765, 767, 768, 771, 772, 775, 776, 777, 779, 782, 783, 784, 786, 788, 789, 792, 794, 795, 798, 799, 800, 803, 804, 805, 806, 807, 808, 809, 810, 812, 815, 816, 817, 818, 819, 820, 823, 825, 826, 827, 828, 829, 831, 836, 839, 840, 842, 843, 844, 845, 846, 847, 851, 852, 853, 854, 855, 856, 858, 859, 862, 863, 864, 866, 867, 869, 870, 873, 874, 875, 877, 881, 882, 883, 884, 885, 887, 888, 889, 891, 893, 894, 895, 898, 899, 900, 901, 902, 903, 904, 906, 907, 909, 912, 913, 914, 916, 918, 919, 921, 922, 923, 929, 932, 933, 934, 935, 936, 937, 939, 940, 941, 942, 946, 950, 951, 953, 954, 956, 957, 958, 960, 961, 963, 965, 967, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 986, 987, 988, 989, 990, 991, 992, 993, 997, 998, 999, 1000, 1001, 1002, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1017, 1020, 1021, 1022, 1023, 1025, 1026, 1028, 1030, 1031, 1032, 1033, 1034, 1036, 1037, 1041, 1042, 1044, 1045, 1046, 1048, 1049, 1051, 1052, 1055, 1057, 1058, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1070, 1071, 1073, 1074, 1075, 1076, 1077, 1078, 1080, 1081, 1082, 1083, 1085, 1086, 1087, 1088, 1092, 1093, 1095, 1096, 1097, 1098, 1099, 1101, 1103, 1104, 1106, 1107, 1110, 1111, 1112, 1113, 1116, 1118, 1119, 1121, 1122, 1125, 1126, 1127, 1128, 1130, 1131, 1132, 1135, 1136, 1138, 1139, 1140, 1141, 1142, 1143, 1145, 1146, 1147, 1149, 1150, 1151, 1153, 1154, 1156, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1180, 1181, 1182, 1183, 1185, 1188, 1189, 1192, 1194, 1195, 1196, 1197, 1198, 1199, 1202, 1205, 1206, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1219, 1220, 1221]

idx_test3=[0, 1, 2, 4, 5, 9, 11, 13, 14, 15, 16, 18, 19, 20, 21, 23, 25, 26, 28, 29, 30, 31, 32, 33, 34, 35, 36, 41, 42, 43, 44, 45, 46, 47, 50, 51, 52, 53, 55, 68, 72, 73, 74, 77, 80, 81, 82, 84, 85, 86, 88, 89, 90, 91, 92, 93, 94, 95, 96, 99, 100, 102, 103, 105, 110, 111, 112, 114, 115, 116, 117, 118, 119, 123, 125, 126, 127, 128, 130, 131, 132, 134, 139, 140, 144, 146, 147, 149, 151, 152, 153, 154, 155, 156, 158, 160, 162, 164, 165, 168, 169, 172, 178, 181, 183, 186, 188, 191, 192, 194, 195, 196, 197, 199, 200, 204, 206, 210, 211, 213, 216, 217, 218, 219, 220, 221, 224, 225, 227, 228, 230, 232, 233, 234, 235, 236, 237, 239, 242, 243, 244, 245, 246, 248, 250, 251, 254, 259, 260, 262, 265, 267, 270, 271, 273, 277, 278, 280, 282, 285, 290, 291, 294, 295, 300, 304, 306, 308, 309, 310, 312, 313, 315, 316, 318, 319, 320, 322, 324, 329, 331, 333, 334, 337, 338, 339, 340, 342, 343, 344, 345, 347, 348, 350, 352, 354, 355, 357, 358, 359, 361, 363, 364, 365, 367, 368, 370, 371, 372, 374, 378, 379, 381, 382, 383, 384, 385, 387, 388, 390, 391, 393, 395, 398, 401, 402, 403, 404, 409, 411, 413, 414, 417, 418, 420, 421, 423, 424, 426, 427, 428, 429, 430, 431, 433, 435, 436, 437, 438, 439, 440, 443, 444, 445, 446, 447, 448, 449, 451, 452, 453, 455, 458, 459, 461, 463, 464, 465, 466, 468, 471, 473, 474, 477, 480, 483, 484, 485, 487, 491, 492, 494, 495, 496, 497, 499, 500, 502, 503, 504, 505, 506, 509, 510, 513, 514, 515, 516, 517, 521, 522, 523, 524, 525, 526, 527, 528, 531, 533, 534, 535, 536, 537, 540, 542, 543, 545, 546, 552, 554, 558, 562, 563, 564, 566, 567, 569, 572, 575, 576, 577, 579, 581, 582, 583, 590, 591, 592, 593, 594, 596, 597, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 613, 614, 616, 618, 619, 620, 621, 622, 623, 627, 628, 629, 630, 632, 634, 635, 636, 637, 642, 644, 645, 646, 648, 649, 650, 651, 653, 654, 656, 657, 658, 659, 660, 661, 662, 664, 665, 666, 668, 669, 670, 671, 672, 673, 674, 675, 677, 678, 680, 681, 683, 685, 686, 687, 688, 689, 690, 691, 692, 694, 695, 698, 700, 704, 705, 706, 708, 710, 711, 712, 714, 715, 717, 718, 719, 720, 721, 723, 724, 725, 727, 728, 730, 731, 733, 734, 735, 736, 738, 740, 741, 742, 743, 744, 745, 746, 747, 749, 752, 754, 755, 759, 761, 762, 763, 765, 767, 768, 771, 772, 775, 776, 777, 780, 782, 783, 784, 785, 787, 788, 789, 790, 792, 795, 798, 799, 800, 802, 803, 804, 805, 806, 807, 808, 810, 811, 813, 815, 817, 819, 820, 821, 823, 824, 825, 826, 827, 828, 829, 830, 831, 836, 839, 840, 842, 843, 844, 845, 846, 847, 848, 850, 851, 852, 853, 854, 855, 858, 859, 862, 863, 864, 866, 867, 868, 869, 870, 871, 873, 874, 875, 876, 878, 879, 880, 881, 882, 883, 884, 885, 887, 888, 889, 891, 893, 897, 898, 899, 900, 901, 903, 904, 906, 907, 908, 909, 910, 911, 913, 914, 915, 916, 917, 918, 919, 921, 922, 924, 925, 926, 927, 928, 929, 932, 933, 934, 935, 937, 938, 940, 941, 944, 948, 949, 950, 951, 953, 955, 956, 957, 960, 961, 962, 963, 965, 967, 970, 971, 972, 974, 975, 976, 978, 979, 980, 982, 986, 987, 988, 989, 990, 991, 992, 993, 996, 998, 1000, 1002, 1004, 1005, 1006, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1017, 1019, 1021, 1023, 1024, 1025, 1028, 1030, 1032, 1033, 1036, 1037, 1039, 1042, 1045, 1048, 1049, 1051, 1052, 1056, 1057, 1058, 1062, 1065, 1067, 1068, 1070, 1071, 1073, 1074, 1076, 1077, 1078, 1080, 1081, 1082, 1084, 1085, 1086, 1087, 1088, 1091, 1092, 1093, 1095, 1096, 1097, 1098, 1099, 1100, 1103, 1104, 1106, 1111, 1112, 1113, 1116, 1118, 1120, 1121, 1122, 1123, 1126, 1127, 1128, 1131, 1132, 1133, 1135, 1136, 1138, 1141, 1142, 1143, 1145, 1147, 1149, 1150, 1153, 1154, 1156, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1168, 1170, 1172, 1173, 1175, 1176, 1181, 1182, 1183, 1185, 1186, 1187, 1188, 1191, 1192, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1202, 1203, 1205, 1206, 1207, 1208, 1209, 1210, 1211, 1212, 1214, 1216, 1217, 1218, 1220]

idx_test4=[0, 1, 2, 3, 5, 6, 8, 9, 11, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 28, 30, 31, 32, 34, 36, 39, 41, 42, 43, 46, 47, 48, 49, 53, 56, 57, 58, 63, 66, 68, 70, 73, 77, 78, 81, 82, 84, 85, 86, 87, 92, 93, 94, 95, 96, 99, 100, 101, 102, 103, 104, 109, 111, 112, 114, 116, 117, 118, 120, 121, 123, 124, 126, 127, 128, 130, 131, 132, 134, 135, 140, 142, 143, 144, 145, 146, 147, 149, 151, 152, 153, 154, 155, 156, 158, 161, 162, 164, 165, 166, 168, 169, 170, 175, 177, 178, 179, 181, 183, 190, 191, 192, 193, 197, 198, 200, 201, 203, 204, 205, 206, 207, 211, 212, 213, 215, 216, 217, 218, 219, 220, 221, 224, 225, 229, 230, 231, 232, 233, 234, 235, 236, 237, 239, 241, 242, 243, 244, 245, 247, 248, 251, 254, 256, 259, 260, 262, 263, 264, 265, 266, 267, 270, 271, 272, 273, 275, 276, 277, 278, 280, 281, 282, 284, 286, 290, 291, 294, 295, 297, 298, 299, 300, 301, 303, 304, 306, 308, 310, 312, 313, 316, 320, 323, 324, 325, 327, 328, 329, 330, 331, 333, 334, 335, 337, 338, 339, 340, 342, 343, 344, 345, 348, 350, 351, 352, 354, 355, 357, 358, 359, 361, 363, 364, 365, 366, 368, 370, 371, 372, 374, 379, 381, 382, 383, 384, 385, 386, 388, 389, 390, 391, 393, 395, 396, 398, 400, 401, 404, 405, 407, 409, 411, 413, 416, 417, 418, 419, 420, 421, 422, 423, 425, 426, 427, 429, 430, 431, 433, 435, 436, 437, 438, 439, 440, 443, 444, 445, 446, 447, 448, 449, 451, 452, 453, 454, 459, 461, 463, 464, 465, 466, 467, 468, 471, 473, 474, 475, 476, 477, 479, 480, 484, 485, 487, 488, 489, 492, 493, 494, 495, 496, 497, 499, 500, 501, 502, 503, 504, 505, 511, 513, 514, 515, 516, 517, 518, 520, 521, 522, 523, 524, 525, 526, 527, 528, 530, 531, 532, 534, 535, 536, 538, 540, 542, 545, 546, 547, 551, 552, 554, 556, 561, 562, 563, 564, 566, 567, 569, 573, 574, 575, 576, 577, 579, 580, 581, 582, 583, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 605, 606, 607, 608, 609, 610, 611, 613, 614, 616, 621, 623, 627, 628, 629, 630, 631, 634, 635, 636, 637, 644, 646, 647, 648, 649, 650, 651, 654, 656, 657, 658, 659, 660, 661, 662, 664, 668, 669, 670, 671, 672, 673, 675, 677, 678, 680, 681, 684, 687, 688, 689, 690, 691, 692, 694, 695, 698, 699, 700, 704, 705, 706, 708, 710, 712, 714, 715, 717, 719, 721, 724, 725, 727, 728, 730, 731, 734, 736, 737, 738, 740, 741, 742, 743, 744, 746, 747, 749, 752, 753, 755, 761, 763, 764, 765, 768, 771, 772, 775, 776, 777, 779, 782, 783, 784, 786, 788, 789, 792, 794, 795, 798, 799, 800, 803, 804, 805, 806, 807, 808, 809, 810, 812, 815, 816, 817, 818, 819, 820, 823, 825, 826, 827, 828, 829, 831, 836, 839, 840, 842, 843, 844, 845, 846, 847, 851, 852, 853, 854, 855, 856, 858, 859, 862, 863, 864, 866, 867, 869, 870, 873, 874, 875, 876, 877, 881, 882, 883, 884, 885, 887, 888, 889, 891, 893, 894, 895, 898, 899, 900, 901, 902, 903, 904, 906, 907, 909, 912, 913, 914, 916, 918, 919, 921, 922, 923, 929, 932, 933, 934, 935, 936, 937, 939, 940, 942, 946, 950, 951, 953, 954, 956, 957, 958, 960, 961, 963, 965, 967, 969, 970, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 986, 987, 988, 989, 990, 991, 992, 993, 997, 998, 999, 1000, 1001, 1002, 1004, 1005, 1006, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1017, 1020, 1021, 1022, 1023, 1025, 1028, 1030, 1031, 1032, 1033, 1034, 1036, 1041, 1042, 1044, 1045, 1048, 1049, 1051, 1052, 1055, 1057, 1058, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1070, 1071, 1073, 1074, 1075, 1076, 1077, 1080, 1081, 1082, 1083, 1085, 1086, 1087, 1092, 1093, 1095, 1096, 1097, 1098, 1099, 1103, 1104, 1106, 1110, 1111, 1112, 1113, 1116, 1118, 1119, 1121, 1122, 1125, 1126, 1127, 1128, 1130, 1131, 1132, 1135, 1136, 1138, 1140, 1141, 1142, 1143, 1145, 1147, 1149, 1150, 1151, 1153, 1154, 1156, 1160, 1161, 1162, 1163, 1164, 1165, 1166, 1167, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1180, 1181, 1183, 1185, 1188, 1189, 1194, 1195, 1196, 1197, 1198, 1199, 1202, 1205, 1206, 1208, 1209, 1210, 1211, 1212, 1213, 1214, 1215, 1216, 1217, 1218, 1220]

idx_test5=[1, 11, 13, 20, 21, 23, 25, 31, 35, 36, 42, 47, 53, 72, 80, 81, 84, 85, 86, 91, 95, 96, 99, 100, 114, 118, 119, 125, 126, 130, 132, 140, 146, 149, 151, 153, 155, 162, 164, 168, 169, 178, 181, 186, 191, 194, 196, 197, 199, 200, 204, 206, 210, 216, 220, 221, 224, 232, 235, 236, 244, 248, 251, 254, 265, 271, 282, 290, 291, 300, 304, 306, 308, 310, 312, 316, 327, 329, 331, 333, 337, 338, 339, 340, 345, 347, 350, 352, 354, 355, 357, 358, 359, 361, 363, 364, 365, 368, 370, 371, 372, 379, 382, 383, 385, 390, 398, 401, 403, 413, 416, 417, 418, 420, 421, 423, 426, 427, 428, 431, 435, 437, 440, 445, 446, 448, 449, 452, 461, 474, 477, 483, 484, 485, 492, 496, 497, 499, 500, 503, 504, 505, 513, 514, 515, 516, 523, 524, 525, 526, 528, 534, 542, 546, 552, 554, 563, 564, 566, 575, 581, 583, 590, 591, 593, 594, 597, 599, 602, 603, 605, 606, 608, 613, 614, 618, 621, 622, 623, 630, 637, 642, 644, 646, 649, 650, 654, 656, 662, 670, 671, 672, 678, 681, 686, 691, 698, 705, 706, 708, 710, 718, 723, 724, 728, 731, 734, 736, 738, 741, 742, 747, 754, 755, 761, 762, 763, 765, 767, 768, 771, 775, 776, 782, 783, 784, 788, 789, 790, 795, 798, 799, 804, 805, 807, 808, 815, 826, 829, 831, 836, 845, 847, 850, 852, 853, 854, 863, 864, 868, 873, 874, 876, 881, 885, 887, 889, 893, 897, 907, 908, 910, 911, 914, 917, 919, 921, 922, 927, 932, 933, 934, 938, 940, 950, 956, 957, 960, 962, 965, 970, 974, 979, 980, 982, 986, 987, 988, 990, 996, 1002, 1005, 1009, 1010, 1013, 1015, 1021, 1028, 1033, 1048, 1049, 1051, 1057, 1058, 1067, 1068, 1070, 1074, 1076, 1078, 1082, 1085, 1086, 1095, 1099, 1103, 1104, 1106, 1118, 1123, 1127, 1131, 1132, 1149, 1154, 1163, 1165, 1167, 1170, 1175, 1192, 1194, 1196, 1197, 1198, 1199, 1211, 1212, 1220]

idx_test6=[0, 1, 3, 6, 8, 11, 13, 15, 16, 17, 18, 19, 20, 23, 25, 30, 31, 32, 36, 42, 47, 48, 49, 56, 58, 66, 68, 84, 85, 86, 92, 93, 94, 96, 99, 100, 101, 102, 103, 107, 109, 112, 114, 118, 120, 121, 123, 126, 127, 128, 131, 132, 134, 140, 143, 146, 147, 149, 151, 153, 154, 155, 159, 162, 164, 165, 166, 168, 169, 170, 177, 178, 179, 181, 190, 191, 197, 200, 203, 204, 206, 207, 212, 216, 219, 220, 221, 224, 225, 229, 230, 231, 245, 247, 248, 251, 254, 259, 265, 266, 267, 270, 271, 277, 280, 282, 286, 290, 291, 295, 297, 300, 303, 304, 306, 308, 310, 311, 313, 316, 320, 324, 327, 328, 329, 330, 331, 333, 334, 337, 338, 339, 340, 342, 345, 350, 351, 352, 354, 357, 358, 359, 361, 363, 364, 365, 368, 370, 371, 372, 374, 379, 382, 383, 385, 386, 388, 389, 391, 393, 395, 398, 401, 404, 405, 407, 411, 413, 417, 418, 420, 421, 423, 427, 435, 436, 437, 438, 439, 440, 443, 444, 445, 447, 448, 449, 459, 461, 463, 466, 467, 468, 471, 473, 474, 477, 478, 480, 484, 485, 486, 488, 489, 492, 493, 494, 495, 496, 499, 500, 502, 505, 513, 514, 516, 517, 523, 524, 526, 528, 530, 531, 535, 538, 540, 541, 542, 545, 546, 548, 551, 552, 554, 556, 561, 562, 563, 564, 566, 567, 576, 579, 581, 582, 590, 591, 593, 594, 596, 597, 598, 599, 601, 602, 605, 609, 610, 611, 614, 617, 623, 627, 628, 631, 635, 636, 637, 644, 646, 649, 650, 651, 654, 656, 657, 658, 660, 662, 668, 669, 671, 672, 673, 675, 680, 681, 687, 688, 692, 695, 697, 698, 699, 705, 706, 708, 710, 717, 719, 721, 724, 727, 728, 730, 731, 734, 738, 740, 741, 742, 743, 746, 747, 749, 752, 753, 756, 761, 765, 771, 775, 776, 777, 779, 782, 783, 784, 786, 788, 789, 792, 798, 799, 800, 803, 805, 806, 807, 808, 810, 815, 817, 819, 820, 823, 825, 826, 827, 828, 829, 831, 836, 839, 840, 842, 843, 845, 847, 858, 862, 863, 864, 867, 870, 873, 874, 876, 881, 883, 884, 887, 888, 889, 893, 894, 895, 898, 900, 902, 903, 904, 906, 907, 909, 912, 913, 914, 916, 919, 921, 922, 923, 929, 932, 933, 934, 936, 940, 946, 950, 956, 957, 960, 965, 967, 972, 974, 975, 976, 977, 979, 980, 982, 986, 987, 988, 990, 991, 992, 993, 998, 999, 1000, 1001, 1002, 1004, 1005, 1006, 1009, 1011, 1012, 1013, 1017, 1021, 1025, 1026, 1028, 1030, 1031, 1032, 1033, 1034, 1036, 1041, 1048, 1049, 1051, 1052, 1063, 1067, 1068, 1070, 1071, 1074, 1075, 1076, 1077, 1081, 1082, 1083, 1087, 1093, 1095, 1098, 1099, 1106, 1107, 1111, 1112, 1113, 1118, 1121, 1122, 1125, 1126, 1127, 1131, 1132, 1136, 1138, 1142, 1143, 1145, 1147, 1149, 1150, 1151, 1153, 1154, 1160, 1161, 1163, 1164, 1165, 1167, 1170, 1171, 1172, 1174, 1175, 1182, 1183, 1185, 1188, 1194, 1196, 1197, 1198, 1199, 1206, 1210, 1211, 1212, 1213, 1214, 1218]
#print("adj.shape[0]",adj.shape[0])
idx_test7=[3, 6, 8, 17, 48, 49, 56, 58, 66, 101, 107, 109, 120, 121, 143, 159, 166, 170, 177, 179, 190, 203, 207, 212, 229, 231, 247, 266, 286, 297, 303, 311, 327, 328, 330, 351, 386, 389, 405, 407, 467, 478, 486, 488, 489, 493, 530, 538, 541, 548, 551, 556, 561, 598, 611, 617, 631, 697, 699, 753, 756, 779, 786, 894, 895, 902, 912, 923, 936, 946, 977, 999, 1001, 1026, 1031, 1034, 1041, 1063, 1075, 1083, 1107, 1125, 1151, 1171, 1174, 1213]

#idx_test8=[3, 6, 8, 17, 22, 39, 48, 49, 56, 57, 58, 63, 66, 70, 78, 87, 101, 104, 109, 120, 121, 124, 135, 142, 143, 145, 161, 166, 170, 175, 177, 179, 190, 193, 198, 201, 203, 205, 207, 212, 215, 229, 231, 241, 247, 256, 263, 264, 266, 272, 275, 276, 281, 284, 286, 297, 298, 299, 301, 303, 323, 325, 327, 328, 330, 335, 351, 366, 386, 389, 396, 400, 405, 407, 416, 419, 422, 425, 454, 467, 475, 476, 479, 488, 489, 493, 501, 511, 518, 520, 530, 532, 538, 547, 551, 556, 561, 573, 574, 580, 595, 598, 611, 631, 647, 684, 699, 737, 753, 779, 786, 794, 809, 812, 816, 818, 856, 877, 894, 895, 902, 912, 923, 936, 939, 942, 946, 954, 958, 969, 973, 977, 981, 997, 999, 1001, 1020, 1022, 1031, 1034, 1041, 1044, 1055, 1063, 1064, 1066, 1075, 1083, 1110, 1119, 1125, 1130, 1140, 1151, 1171, 1174, 1180, 1189, 1213, 1215]

idx_test8=[4, 29, 33, 35, 44, 45, 50, 51, 52, 72, 74, 80, 91, 105, 110, 119, 125, 160, 172, 186, 194, 196, 199, 227, 228, 246, 250, 285, 322, 347, 378, 387, 402, 403, 414, 424, 428, 458, 483, 491, 506, 510, 533, 543, 558, 603, 604, 618, 619, 620, 622, 632, 642, 645, 653, 665, 666, 674, 683, 685, 686, 711, 718, 723, 733, 735, 745, 754, 759, 762, 767, 780, 785, 787, 790, 802, 811, 813, 821, 824, 830, 848, 850, 868, 878, 880, 897, 908, 910, 911, 915, 917, 924, 925, 926, 927, 928, 938, 941, 944, 949, 955, 962, 996, 1024, 1039, 1056, 1078, 1079, 1084, 1088, 1091, 1100, 1120, 1123, 1133, 1168, 1186, 1187, 1191, 1192, 1200, 1203, 1207]


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
#acc [0.9417177914110431, 0.9447852760736197, 0.9447852760736197, 0.9447852760736197]

#neighbor type 1:
#acc [0.9560117302052786, 0.9442815249266863, 0.9516129032258065, 0.9604105571847508]

#neighbor type 2:
#acc [0.9502427184466019, 0.9526699029126213, 0.9502427184466019, 0.9502427184466019]

#neighbor type 3:
#acc [0.9512516469038208, 0.9407114624505929, 0.9459815546772069, 0.9552042160737814]
    
#neighbor type 4:
#acc [0.9544863459037711, 0.9440832249674903, 0.9570871261378414, 0.9622886866059818]

#neighbor type 5:
#acc [0.9616519174041298, 0.9498525073746312, 0.9557522123893805, 0.9557522123893805]

#neighbor type 6:
#acc [0.9515503875968992, 0.9651162790697674, 0.9670542635658914, 0.9670542635658914]

#neighbor type 7:
#acc [0.9069767441860465, 0.9186046511627907, 0.9186046511627907, 0.9186046511627907]

#neighbor type 8:
#acc [0.93125, 0.925, 0.9437500000000001, 0.925]

#neighbor type 8-0:
#acc [0.9274193548387096, 0.5887096774193549, 0.7338709677419355, 0.782258064516129]


