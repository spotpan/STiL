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
parser.add_argument('--seed', type=int, default=18, help='Random seed.')
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


idx_test1=[4, 5, 7, 12, 13, 15, 16, 18, 19, 21, 23, 24, 27, 28, 31, 32, 33, 34, 37, 41, 42, 46, 47, 50, 52, 53, 60, 61, 62, 64, 65, 68, 69, 71, 72, 73, 75, 76, 79, 80, 81, 83, 84, 85, 86, 91, 92, 94, 95, 96, 99, 100, 103, 108, 110, 111, 112, 114, 116, 117, 119, 122, 123, 125, 127, 128, 130, 132, 136, 137, 138, 140, 146, 149, 150, 151, 153, 155, 156, 157, 158, 160, 162, 164, 165, 168, 169, 173, 176, 178, 180, 183, 184, 191, 192, 194, 195, 196, 197, 199, 200, 202, 204, 206, 208, 211, 214, 216, 217, 218, 221, 223, 224, 225, 227, 234, 235, 242, 244, 245, 248, 249, 250, 257, 258, 259, 260, 261, 265, 267, 268, 269, 273, 278, 279, 282, 285, 287, 288, 290, 291, 293, 295, 300, 302, 304, 306, 307, 308, 310, 312, 313, 315, 316, 317, 320, 322, 326, 329, 331, 332, 334, 336, 338, 339, 340, 342, 344, 345, 346, 350, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 368, 371, 372, 373, 375, 376, 378, 379, 380, 381, 383, 384, 387, 388, 393, 395, 398, 402, 403, 404, 406, 411, 414, 415, 418, 421, 424, 426, 427, 428, 430, 431, 432, 435, 436, 437, 438, 440, 441, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 456, 458, 459, 460, 461, 463, 464, 465, 466, 468, 469, 470, 471, 472, 473, 474, 477, 481, 482, 483, 484, 485, 487, 490, 491, 492, 494, 495, 497, 499, 500, 503, 508, 512, 515, 517, 521, 523, 524, 525, 526, 527, 533, 534, 535, 542, 543, 545, 546, 549, 552, 553, 554, 557, 558, 560, 562, 563, 565, 566, 567, 569, 571, 575, 576, 577, 578, 581, 582, 583, 589, 590, 591, 592, 593, 594, 596, 597, 599, 600, 601, 603, 604, 606, 607, 608, 609, 610, 612, 613, 614, 615, 616, 618, 621, 622, 623, 626, 627, 629, 630, 632, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 648, 649, 650, 651, 652, 653, 654, 656, 659, 660, 661, 662, 665, 668, 669, 670, 671, 673, 674, 675, 676, 677, 679, 681, 684, 685, 686, 687, 688, 691, 693, 694, 695, 696, 698, 701, 704, 705, 707, 710, 711, 712, 713, 714, 716, 717, 718, 723, 725, 726, 727, 728, 731, 733, 734, 736, 738, 739, 740, 741, 743, 745, 746, 747, 749, 752, 754, 755, 757, 759, 760, 761, 765, 766, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 782, 784, 785, 788, 789, 790, 791, 792, 793, 795, 796, 798, 799, 802, 803, 804, 805, 806, 807, 808, 810, 813, 814, 815, 817, 820, 822, 823, 824, 825, 826, 827, 828, 829, 830, 834, 836, 840, 841, 845, 846, 847, 848, 849, 850, 852, 853, 854, 858, 859, 862, 863, 864, 868, 869, 870, 871, 872, 874, 875, 878, 881, 882, 883, 884, 885, 886, 887, 889, 893, 896, 898, 899, 900, 901, 903, 904, 905, 906, 907, 908, 909, 911, 913, 915, 916, 918, 919, 920, 921, 924, 926, 927, 928, 929, 930, 931, 932, 933, 935, 938, 941, 943, 944, 947, 949, 950, 955, 956, 957, 959, 960, 961, 962, 964, 965, 966, 967, 970, 971, 974, 975, 976, 979, 980, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 996, 998, 1000, 1002, 1004, 1006, 1009, 1010, 1012, 1013, 1015, 1016, 1017, 1023, 1024, 1025, 1027, 1028, 1029, 1030, 1032, 1033, 1035, 1036, 1038, 1042, 1043, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1056, 1058, 1059, 1060, 1062, 1065, 1067, 1071, 1072, 1074, 1076, 1077, 1079, 1080, 1082, 1084, 1085, 1086, 1087, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1104, 1105, 1106, 1112, 1113, 1114, 1115, 1116, 1117, 1120, 1123, 1124, 1127, 1131, 1132, 1133, 1136, 1141, 1143, 1145, 1147, 1150, 1152, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1165, 1166, 1167, 1168, 1169, 1170, 1172, 1173, 1175, 1176, 1177, 1178, 1181, 1183, 1184, 1185, 1188, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1202, 1203, 1204, 1205, 1207, 1208, 1209, 1211, 1212, 1218, 1220]

idx_test2=[2, 5, 7, 9, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 27, 28, 31, 32, 34, 37, 39, 41, 42, 46, 47, 48, 49, 52, 53, 56, 57, 58, 60, 61, 62, 63, 65, 66, 67, 68, 71, 73, 75, 76, 77, 78, 79, 81, 82, 83, 84, 85, 86, 87, 92, 93, 94, 95, 96, 98, 99, 100, 101, 102, 103, 104, 106, 107, 108, 109, 111, 112, 113, 114, 116, 117, 120, 121, 122, 123, 124, 127, 128, 130, 131, 132, 133, 135, 136, 137, 138, 140, 143, 144, 145, 146, 148, 149, 151, 153, 155, 156, 158, 159, 161, 162, 164, 165, 168, 169, 170, 174, 176, 177, 178, 179, 180, 182, 183, 184, 185, 187, 191, 192, 194, 197, 200, 201, 202, 203, 204, 206, 208, 211, 212, 215, 216, 217, 218, 221, 222, 223, 224, 225, 226, 229, 231, 233, 234, 235, 238, 240, 241, 242, 244, 245, 247, 248, 249, 253, 255, 256, 257, 258, 259, 260, 261, 263, 264, 265, 266, 267, 268, 269, 273, 275, 277, 278, 281, 282, 283, 284, 287, 288, 289, 290, 291, 292, 293, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 306, 307, 308, 310, 312, 313, 314, 316, 317, 320, 323, 324, 325, 326, 328, 329, 331, 332, 334, 335, 338, 339, 340, 341, 342, 344, 345, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 361, 362, 363, 364, 365, 366, 368, 369, 371, 372, 373, 375, 376, 377, 379, 380, 381, 383, 384, 386, 388, 389, 392, 393, 395, 396, 397, 398, 399, 400, 404, 405, 406, 407, 411, 412, 415, 416, 418, 419, 421, 422, 425, 426, 427, 430, 431, 432, 434, 435, 436, 437, 438, 440, 441, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 456, 458, 459, 460, 461, 463, 464, 465, 466, 467, 468, 469, 470, 471, 473, 474, 475, 476, 477, 479, 481, 482, 484, 485, 486, 487, 488, 489, 490, 492, 493, 494, 495, 497, 498, 499, 500, 501, 503, 507, 508, 511, 512, 515, 517, 518, 520, 521, 523, 524, 525, 526, 527, 528, 530, 531, 532, 534, 535, 538, 542, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 556, 559, 560, 561, 562, 563, 565, 566, 567, 568, 569, 571, 573, 575, 576, 577, 578, 581, 582, 583, 584, 587, 589, 590, 591, 592, 593, 594, 595, 596, 597, 599, 600, 601, 606, 607, 608, 609, 610, 611, 612, 613, 614, 616, 617, 621, 622, 623, 624, 626, 627, 628, 629, 630, 632, 634, 635, 636, 637, 638, 640, 641, 642, 643, 644, 646, 647, 648, 649, 650, 651, 652, 654, 655, 656, 659, 660, 661, 662, 663, 667, 668, 669, 670, 671, 673, 675, 676, 677, 679, 680, 681, 684, 687, 688, 689, 690, 691, 693, 694, 695, 696, 697, 698, 703, 704, 705, 707, 709, 710, 711, 712, 713, 714, 716, 717, 718, 722, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 736, 737, 738, 739, 740, 741, 743, 746, 747, 748, 749, 752, 753, 755, 756, 757, 760, 761, 762, 765, 766, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 782, 784, 788, 789, 791, 792, 793, 794, 795, 797, 798, 799, 800, 801, 803, 804, 805, 806, 807, 808, 809, 810, 812, 814, 815, 816, 817, 818, 820, 823, 825, 826, 827, 828, 829, 834, 836, 840, 841, 842, 843, 844, 845, 846, 847, 849, 852, 853, 854, 858, 859, 860, 861, 862, 863, 864, 865, 869, 870, 872, 874, 875, 881, 882, 883, 884, 885, 886, 887, 889, 890, 893, 894, 896, 898, 899, 900, 901, 903, 904, 905, 906, 907, 909, 912, 913, 916, 918, 919, 920, 921, 923, 927, 929, 930, 931, 932, 933, 935, 936, 941, 942, 943, 946, 950, 951, 954, 956, 957, 958, 959, 960, 961, 963, 964, 965, 966, 967, 969, 970, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 997, 998, 999, 1000, 1001, 1002, 1004, 1006, 1008, 1009, 1010, 1012, 1013, 1015, 1016, 1017, 1018, 1022, 1023, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1035, 1036, 1037, 1038, 1040, 1042, 1043, 1044, 1046, 1047, 1048, 1049, 1051, 1052, 1053, 1054, 1055, 1057, 1058, 1059, 1060, 1062, 1063, 1064, 1065, 1066, 1067, 1069, 1071, 1072, 1074, 1075, 1076, 1077, 1080, 1082, 1083, 1085, 1086, 1087, 1089, 1090, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1101, 1102, 1104, 1105, 1106, 1110, 1112, 1113, 1114, 1115, 1116, 1117, 1119, 1122, 1124, 1125, 1127, 1128, 1130, 1131, 1132, 1136, 1138, 1139, 1140, 1141, 1143, 1144, 1145, 1146, 1147, 1148, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1159, 1160, 1161, 1162, 1165, 1166, 1167, 1169, 1170, 1171, 1172, 1174, 1175, 1176, 1177, 1178, 1180, 1181, 1182, 1183, 1184, 1185, 1188, 1189, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1202, 1204, 1205, 1206, 1208, 1209, 1211, 1212, 1213, 1218, 1219, 1220]

idx_test3=[4, 5, 7, 9, 12, 13, 14, 15, 16, 18, 19, 21, 23, 24, 26, 27, 28, 31, 32, 33, 34, 37, 41, 42, 44, 45, 46, 47, 50, 52, 53, 55, 60, 61, 62, 64, 65, 68, 69, 71, 72, 73, 75, 76, 79, 80, 81, 82, 83, 84, 85, 86, 88, 89, 90, 91, 92, 93, 94, 95, 96, 99, 100, 102, 103, 106, 108, 110, 111, 112, 114, 116, 117, 119, 122, 123, 125, 127, 128, 130, 131, 132, 136, 137, 138, 140, 144, 146, 149, 150, 151, 153, 155, 156, 157, 158, 160, 162, 164, 165, 168, 169, 173, 176, 178, 179, 180, 183, 184, 188, 191, 192, 194, 195, 196, 197, 199, 200, 202, 204, 206, 208, 209, 210, 211, 214, 216, 217, 218, 221, 223, 224, 225, 227, 233, 234, 235, 242, 244, 245, 248, 249, 250, 257, 258, 259, 260, 261, 265, 267, 268, 269, 273, 277, 278, 279, 282, 285, 287, 288, 290, 291, 293, 295, 300, 302, 304, 305, 306, 307, 308, 310, 312, 313, 315, 316, 317, 318, 319, 320, 322, 324, 326, 329, 331, 332, 334, 336, 338, 339, 340, 342, 344, 345, 346, 350, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 367, 368, 371, 372, 373, 375, 376, 378, 379, 380, 381, 383, 384, 387, 388, 393, 395, 397, 398, 402, 403, 404, 406, 410, 411, 414, 415, 418, 421, 424, 426, 427, 428, 430, 431, 432, 433, 435, 436, 437, 438, 440, 441, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 455, 456, 458, 459, 460, 461, 463, 464, 465, 466, 468, 469, 470, 471, 472, 473, 474, 477, 481, 482, 483, 484, 485, 487, 490, 491, 492, 494, 495, 497, 499, 500, 503, 508, 509, 510, 512, 515, 517, 521, 522, 523, 524, 525, 526, 527, 528, 529, 531, 533, 534, 535, 536, 537, 542, 543, 545, 546, 549, 552, 553, 554, 558, 562, 563, 565, 566, 567, 569, 571, 572, 575, 576, 577, 578, 581, 582, 583, 589, 590, 591, 592, 593, 594, 596, 597, 599, 600, 601, 603, 604, 606, 607, 608, 609, 610, 612, 613, 614, 616, 618, 620, 621, 622, 623, 626, 627, 628, 629, 630, 632, 634, 635, 636, 637, 638, 639, 642, 643, 644, 645, 646, 648, 649, 650, 651, 652, 653, 654, 656, 659, 660, 661, 662, 665, 668, 669, 670, 671, 673, 674, 675, 676, 677, 679, 680, 681, 682, 685, 686, 687, 688, 689, 690, 691, 693, 694, 695, 696, 698, 701, 704, 705, 707, 710, 711, 712, 713, 714, 716, 717, 718, 720, 723, 724, 725, 726, 727, 728, 730, 731, 733, 734, 736, 738, 739, 740, 741, 743, 745, 746, 747, 748, 749, 752, 754, 755, 757, 759, 760, 761, 762, 765, 766, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 780, 782, 784, 785, 788, 789, 790, 791, 792, 793, 795, 796, 798, 799, 800, 802, 803, 804, 805, 806, 807, 808, 810, 813, 814, 815, 817, 820, 822, 823, 824, 825, 826, 827, 828, 829, 830, 833, 834, 836, 840, 841, 844, 845, 846, 847, 848, 849, 850, 852, 853, 854, 858, 859, 862, 863, 864, 868, 869, 870, 871, 872, 874, 875, 878, 879, 881, 882, 883, 884, 885, 886, 887, 889, 893, 896, 898, 899, 900, 901, 903, 904, 905, 906, 907, 908, 909, 911, 913, 915, 916, 918, 919, 920, 921, 924, 926, 927, 929, 930, 931, 932, 933, 935, 938, 941, 943, 944, 947, 949, 950, 955, 956, 957, 959, 960, 961, 962, 963, 964, 965, 966, 967, 970, 971, 974, 975, 976, 978, 979, 980, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 996, 998, 1000, 1002, 1004, 1006, 1008, 1009, 1010, 1012, 1013, 1015, 1016, 1017, 1023, 1024, 1025, 1027, 1028, 1029, 1030, 1032, 1033, 1035, 1036, 1038, 1042, 1043, 1047, 1048, 1049, 1050, 1051, 1052, 1053, 1056, 1057, 1058, 1059, 1060, 1062, 1065, 1067, 1071, 1072, 1074, 1076, 1077, 1079, 1080, 1082, 1084, 1085, 1086, 1087, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1104, 1105, 1106, 1112, 1113, 1114, 1115, 1116, 1117, 1120, 1122, 1123, 1124, 1127, 1128, 1131, 1132, 1133, 1136, 1138, 1141, 1143, 1145, 1147, 1148, 1150, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1162, 1165, 1166, 1167, 1168, 1169, 1170, 1172, 1173, 1175, 1176, 1177, 1178, 1181, 1182, 1183, 1184, 1185, 1188, 1192, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1200, 1202, 1203, 1204, 1205, 1206, 1207, 1208, 1209, 1211, 1212, 1218, 1220]

idx_test4=[2, 5, 7, 9, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 27, 28, 31, 32, 34, 37, 39, 41, 42, 46, 47, 48, 49, 52, 53, 56, 57, 58, 60, 61, 63, 65, 66, 67, 68, 71, 73, 75, 76, 77, 78, 79, 81, 82, 83, 84, 85, 86, 87, 92, 93, 94, 95, 96, 98, 99, 100, 101, 102, 103, 104, 108, 109, 111, 112, 113, 114, 116, 117, 120, 121, 122, 123, 124, 127, 128, 130, 131, 132, 133, 135, 136, 137, 138, 140, 143, 144, 145, 146, 149, 151, 153, 155, 156, 158, 159, 161, 162, 164, 165, 168, 169, 170, 174, 176, 177, 178, 179, 180, 183, 184, 185, 187, 191, 192, 197, 200, 201, 202, 203, 204, 206, 208, 209, 211, 212, 215, 216, 217, 218, 221, 223, 224, 225, 226, 229, 231, 233, 234, 235, 238, 240, 241, 242, 244, 245, 247, 248, 249, 256, 257, 258, 259, 260, 261, 263, 264, 265, 266, 267, 268, 269, 273, 275, 277, 278, 281, 282, 283, 284, 287, 288, 289, 290, 291, 292, 293, 295, 297, 298, 299, 300, 301, 302, 303, 304, 306, 307, 308, 310, 312, 313, 314, 316, 317, 320, 323, 324, 325, 326, 328, 329, 331, 334, 335, 338, 339, 340, 341, 342, 344, 345, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 361, 362, 363, 364, 365, 366, 368, 371, 372, 373, 375, 376, 377, 379, 380, 381, 383, 384, 386, 388, 389, 392, 393, 395, 396, 397, 398, 400, 404, 405, 406, 407, 411, 412, 415, 416, 418, 419, 421, 422, 425, 426, 427, 430, 431, 432, 433, 434, 435, 436, 437, 438, 440, 441, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 459, 460, 461, 463, 464, 465, 466, 468, 470, 471, 473, 474, 475, 476, 477, 479, 481, 482, 484, 485, 487, 488, 489, 490, 492, 493, 494, 495, 497, 499, 500, 501, 503, 507, 508, 511, 512, 515, 517, 518, 520, 521, 522, 523, 524, 525, 526, 527, 528, 530, 531, 532, 534, 535, 536, 538, 542, 544, 545, 546, 547, 549, 550, 551, 552, 553, 554, 556, 559, 560, 561, 562, 563, 565, 566, 567, 569, 571, 573, 575, 576, 577, 581, 582, 583, 587, 589, 590, 591, 592, 593, 594, 595, 596, 597, 599, 600, 601, 606, 607, 608, 609, 610, 611, 612, 613, 614, 616, 621, 622, 623, 624, 626, 627, 628, 629, 630, 632, 634, 635, 636, 637, 638, 642, 643, 644, 646, 647, 648, 649, 650, 651, 652, 654, 655, 656, 659, 660, 661, 662, 663, 667, 668, 669, 670, 671, 673, 675, 676, 677, 679, 680, 681, 684, 687, 688, 689, 690, 691, 693, 694, 695, 696, 698, 704, 705, 707, 709, 710, 712, 713, 714, 716, 717, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 736, 737, 738, 739, 740, 741, 743, 746, 747, 748, 749, 752, 753, 755, 757, 760, 761, 762, 765, 766, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 782, 784, 788, 789, 791, 792, 793, 794, 795, 797, 798, 799, 800, 801, 803, 804, 805, 806, 807, 808, 809, 810, 812, 814, 815, 816, 817, 818, 820, 823, 825, 826, 827, 828, 829, 834, 836, 840, 841, 842, 843, 844, 845, 846, 847, 849, 852, 853, 854, 858, 859, 860, 862, 863, 864, 865, 869, 870, 872, 874, 875, 881, 882, 883, 884, 885, 886, 887, 889, 890, 893, 894, 896, 898, 899, 900, 901, 903, 904, 905, 906, 907, 909, 912, 913, 916, 918, 919, 920, 921, 923, 929, 930, 931, 932, 933, 935, 936, 941, 942, 943, 946, 950, 951, 954, 956, 957, 958, 959, 960, 961, 963, 964, 965, 966, 967, 969, 970, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 997, 998, 999, 1000, 1001, 1002, 1004, 1006, 1008, 1009, 1010, 1012, 1013, 1015, 1016, 1017, 1022, 1023, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1035, 1036, 1037, 1038, 1040, 1042, 1043, 1048, 1049, 1051, 1052, 1053, 1054, 1055, 1057, 1058, 1059, 1060, 1062, 1063, 1064, 1065, 1066, 1067, 1069, 1071, 1072, 1074, 1075, 1076, 1077, 1080, 1082, 1083, 1085, 1086, 1087, 1089, 1090, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1101, 1102, 1104, 1105, 1106, 1110, 1112, 1113, 1114, 1115, 1116, 1117, 1119, 1122, 1124, 1125, 1127, 1128, 1130, 1131, 1132, 1136, 1138, 1139, 1140, 1141, 1143, 1144, 1145, 1146, 1147, 1148, 1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1159, 1160, 1161, 1162, 1165, 1166, 1167, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177, 1178, 1180, 1181, 1183, 1184, 1185, 1188, 1189, 1193, 1194, 1195, 1196, 1197, 1198, 1199, 1202, 1204, 1205, 1206, 1208, 1209, 1211, 1212, 1213, 1218, 1219, 1220]

idx_test5=[5, 12, 13, 15, 16, 18, 19, 21, 23, 27, 31, 41, 42, 46, 47, 53, 61, 64, 65, 71, 73, 75, 76, 77, 81, 83, 85, 86, 89, 90, 91, 92, 95, 96, 99, 100, 108, 112, 114, 117, 119, 122, 125, 127, 130, 131, 132, 136, 137, 138, 140, 146, 150, 151, 153, 155, 162, 164, 165, 168, 169, 176, 178, 179, 183, 184, 194, 196, 197, 202, 204, 206, 208, 214, 216, 224, 242, 244, 245, 258, 259, 261, 265, 268, 269, 279, 282, 285, 288, 290, 291, 300, 302, 304, 306, 307, 308, 310, 313, 316, 320, 326, 332, 338, 339, 340, 344, 345, 350, 353, 356, 357, 358, 359, 361, 363, 364, 368, 371, 372, 373, 375, 376, 379, 380, 383, 388, 398, 403, 406, 411, 418, 421, 426, 427, 432, 435, 436, 438, 440, 441, 444, 445, 446, 448, 449, 450, 452, 456, 459, 461, 464, 466, 469, 470, 472, 473, 477, 482, 483, 485, 492, 494, 495, 497, 499, 500, 503, 515, 521, 523, 524, 525, 534, 542, 545, 546, 552, 554, 562, 563, 565, 566, 569, 571, 575, 576, 581, 583, 590, 591, 593, 594, 596, 597, 599, 601, 603, 606, 607, 608, 613, 618, 621, 622, 630, 634, 637, 638, 640, 641, 642, 644, 646, 650, 654, 656, 661, 668, 670, 671, 680, 681, 686, 689, 691, 696, 698, 701, 705, 710, 711, 712, 718, 723, 727, 728, 731, 734, 736, 738, 739, 740, 747, 752, 755, 757, 761, 762, 765, 768, 770, 774, 775, 776, 777, 782, 788, 789, 790, 791, 793, 795, 796, 798, 799, 805, 815, 820, 825, 826, 829, 834, 836, 841, 845, 847, 850, 852, 853, 854, 863, 864, 868, 874, 875, 881, 885, 887, 889, 896, 898, 907, 908, 916, 919, 920, 921, 924, 927, 928, 932, 938, 941, 950, 956, 960, 962, 966, 971, 974, 979, 980, 982, 983, 984, 986, 987, 988, 993, 994, 1009, 1010, 1013, 1015, 1017, 1019, 1027, 1028, 1029, 1035, 1047, 1048, 1049, 1053, 1057, 1058, 1067, 1074, 1076, 1085, 1086, 1095, 1104, 1105, 1106, 1117, 1123, 1127, 1132, 1136, 1141, 1143, 1152, 1154, 1155, 1158, 1159, 1166, 1167, 1169, 1170, 1175, 1177, 1184, 1192, 1196, 1198, 1199, 1203, 1205, 1208, 1209, 1211, 1212, 1220]

idx_test6=[7, 12, 13, 15, 16, 17, 18, 19, 21, 23, 27, 31, 32, 37, 42, 47, 48, 52, 56, 60, 61, 62, 65, 68, 71, 73, 75, 76, 78, 83, 84, 85, 87, 92, 93, 94, 96, 98, 99, 102, 103, 106, 109, 111, 112, 113, 114, 120, 121, 122, 123, 127, 131, 132, 136, 137, 140, 143, 144, 145, 146, 148, 149, 151, 153, 155, 156, 158, 159, 162, 164, 165, 168, 169, 170, 174, 176, 177, 179, 180, 182, 183, 184, 185, 191, 192, 197, 200, 202, 203, 204, 206, 208, 215, 216, 221, 222, 224, 225, 229, 231, 233, 234, 235, 238, 242, 245, 247, 248, 249, 259, 261, 264, 266, 268, 269, 277, 282, 287, 288, 289, 290, 291, 293, 295, 297, 300, 301, 302, 303, 304, 306, 307, 308, 310, 313, 316, 317, 320, 324, 326, 331, 334, 335, 338, 339, 340, 344, 345, 350, 352, 353, 354, 355, 357, 358, 359, 361, 362, 363, 364, 365, 368, 369, 371, 372, 373, 375, 376, 379, 380, 383, 388, 389, 393, 398, 399, 400, 404, 406, 411, 418, 421, 426, 427, 430, 435, 436, 437, 438, 440, 441, 443, 444, 445, 447, 448, 449, 452, 454, 456, 459, 460, 461, 463, 464, 465, 466, 468, 470, 471, 473, 474, 476, 477, 479, 481, 482, 485, 488, 490, 493, 495, 497, 498, 499, 500, 503, 507, 511, 512, 518, 523, 524, 525, 528, 532, 535, 542, 545, 546, 550, 551, 552, 554, 562, 563, 565, 566, 567, 568, 569, 571, 573, 575, 576, 581, 582, 583, 587, 589, 590, 591, 594, 596, 597, 599, 601, 606, 607, 608, 609, 610, 612, 614, 616, 621, 622, 624, 626, 627, 628, 629, 632, 634, 635, 636, 637, 638, 642, 643, 644, 646, 647, 648, 649, 650, 652, 654, 655, 656, 662, 663, 667, 668, 669, 670, 671, 673, 680, 681, 684, 687, 688, 689, 690, 691, 693, 694, 698, 703, 704, 705, 709, 710, 712, 713, 714, 716, 717, 722, 726, 727, 728, 729, 730, 731, 732, 733, 734, 736, 737, 738, 739, 740, 741, 743, 746, 748, 749, 752, 753, 755, 757, 760, 761, 765, 770, 771, 772, 773, 774, 775, 777, 778, 779, 782, 784, 788, 792, 793, 794, 797, 798, 799, 800, 801, 804, 806, 807, 808, 810, 814, 817, 820, 823, 825, 826, 827, 828, 829, 834, 836, 840, 841, 845, 846, 847, 849, 858, 859, 860, 861, 863, 864, 865, 870, 872, 874, 875, 881, 883, 884, 886, 887, 889, 890, 893, 894, 900, 901, 903, 904, 905, 906, 907, 909, 912, 913, 916, 918, 919, 920, 921, 923, 929, 930, 931, 932, 935, 936, 941, 943, 946, 950, 951, 956, 957, 958, 959, 960, 964, 965, 967, 969, 974, 977, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 991, 992, 993, 994, 997, 998, 999, 1000, 1001, 1002, 1004, 1006, 1008, 1009, 1012, 1013, 1016, 1017, 1022, 1025, 1027, 1028, 1029, 1030, 1033, 1035, 1036, 1037, 1038, 1040, 1042, 1043, 1048, 1049, 1051, 1053, 1054, 1060, 1062, 1063, 1064, 1066, 1067, 1069, 1071, 1072, 1074, 1075, 1076, 1077, 1080, 1082, 1083, 1086, 1087, 1089, 1093, 1094, 1095, 1098, 1104, 1105, 1106, 1114, 1115, 1116, 1117, 1119, 1124, 1125, 1127, 1130, 1131, 1132, 1136, 1138, 1139, 1143, 1144, 1145, 1146, 1147, 1148, 1150, 1151, 1152, 1153, 1154, 1155, 1160, 1161, 1165, 1166, 1167, 1169, 1170, 1171, 1172, 1174, 1175, 1177, 1178, 1180, 1181, 1183, 1184, 1185, 1188, 1193, 1194, 1196, 1197, 1198, 1199, 1204, 1206, 1208, 1211, 1212, 1218, 1220]
#print("adj.shape[0]",adj.shape[0])
idx_test7=[17, 48, 56, 78, 87, 98, 109, 113, 120, 121, 143, 145, 148, 159, 170, 174, 177, 182, 185, 203, 215, 222, 229, 231, 238, 247, 264, 266, 289, 297, 301, 303, 335, 369, 389, 399, 400, 454, 476, 479, 488, 493, 498, 507, 511, 518, 532, 550, 551, 568, 573, 587, 624, 647, 655, 663, 667, 703, 709, 722, 729, 732, 737, 753, 779, 794, 797, 801, 860, 861, 865, 890, 894, 912, 923, 936, 946, 951, 958, 969, 977, 981, 997, 999, 1001, 1022, 1037, 1040, 1054, 1063, 1064, 1066, 1069, 1075, 1083, 1089, 1119, 1125, 1130, 1139, 1144, 1146, 1151, 1171, 1174, 1180]

#idx_test8=[2, 17, 22, 39, 48, 49, 56, 57, 58, 63, 66, 67, 77, 78, 87, 98, 101, 104, 109, 113, 120, 121, 124, 133, 135, 143, 145, 159, 161, 170, 174, 177, 185, 187, 201, 203, 212, 215, 226, 229, 231, 238, 240, 241, 247, 256, 263, 264, 266, 275, 281, 283, 284, 289, 292, 297, 298, 299, 301, 303, 314, 323, 325, 328, 335, 341, 349, 351, 366, 377, 386, 389, 392, 396, 400, 405, 407, 412, 416, 419, 422, 425, 434, 453, 454, 475, 476, 479, 488, 489, 493, 501, 507, 511, 518, 520, 530, 532, 538, 544, 547, 550, 551, 556, 559, 561, 573, 587, 595, 611, 624, 647, 655, 663, 667, 709, 729, 732, 737, 753, 779, 794, 797, 801, 809, 812, 816, 818, 842, 843, 860, 865, 890, 894, 912, 923, 936, 942, 946, 951, 954, 958, 969, 977, 981, 997, 999, 1001, 1022, 1026, 1031, 1037, 1040, 1054, 1055, 1063, 1064, 1066, 1069, 1075, 1083, 1089, 1090, 1101, 1102, 1110, 1119, 1125, 1130, 1139, 1140, 1144, 1146, 1151, 1171, 1174, 1180, 1189, 1213, 1219]

idx_test8=[4, 33, 50, 64, 69, 72, 80, 91, 110, 119, 125, 150, 157, 160, 173, 194, 195, 196, 199, 214, 227, 250, 279, 285, 315, 322, 332, 336, 346, 360, 378, 387, 402, 403, 414, 424, 428, 458, 469, 472, 483, 491, 533, 543, 557, 558, 578, 603, 604, 615, 618, 639, 640, 641, 645, 653, 665, 674, 685, 686, 701, 711, 718, 723, 745, 754, 759, 785, 790, 796, 802, 813, 822, 824, 830, 848, 850, 868, 871, 878, 908, 911, 915, 924, 926, 927, 928, 938, 944, 947, 949, 955, 962, 971, 996, 1024, 1047, 1050, 1056, 1079, 1084, 1091, 1120, 1123, 1133, 1158, 1168, 1192, 1200, 1203, 1207]

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
#acc [0.9345603271983641, 0.9335378323108385, 0.9335378323108385, 0.9304703476482619]

#neighbor type 1:
#acc [0.9515669515669516, 0.9515669515669516, 0.952991452991453, 0.952991452991453]

#neighbor type 2:
#acc [0.9394299287410927, 0.9299287410926366, 0.9346793349168646, 0.9429928741092637]

#neighbor type 3:
#acc [0.9448094612352168, 0.9448094612352168, 0.9448094612352168, 0.9448094612352168]
    
#neighbor type 4:
#acc [0.9493201483312731, 0.938195302843016, 0.9245982694684796, 0.9530284301606922]

#neighbor type 5:
#acc [0.9680851063829787, 0.9627659574468085, 0.9627659574468085, 0.9627659574468085]

#neighbor type 6:
#acc [0.9404761904761905, 0.9370748299319728, 0.9404761904761905, 0.9438775510204082]

#neighbor type 7:
#acc [0.8584905660377358, 0.8679245283018867, 0.8584905660377358, 0.8396226415094339]

#neighbor type 8:
#acc [0.9222222222222223, 0.9222222222222223, 0.9166666666666667, 0.9055555555555556]

#neighbor type 8-0:
#acc [0.9279279279279279, 0.9009009009009009, 0.9009009009009009, 0.9009009009009009]

