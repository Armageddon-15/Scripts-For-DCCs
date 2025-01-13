TRANSLATE_TEXT = {
    # ---- Public ----
    "x-axis":
        {"en": "X Axis",
         "zh": "X 轴"},
    "y-axis":
        {"en": "Y Axis",
         "zh": "Y 轴"},
    "z-axis":
        {"en": "Z Axis",
         "zh": "Z 轴"},
    "pivot_x":
        {"en": "Pivot X",
         "zh": "X 枢轴"},
    "pivot_y":
        {"en": "Pivot Y",
         "zh": "Y 枢轴"},
    "pivot_z":
        {"en": "Pivot Z",
         "zh": "Z 枢轴"},
    "Apply":
        {"zh": "应用"},
    "Get":
        {"zh": "获取"},
    "Searching Method:":
        {"zh": "寻找方法："},
    # "":
    #     {"zh": ""},
    # ---- Title ----
    "Adv Assistance":
        {"zh": "ADV 辅助"},
    "Bake Preparation":
        {"zh": "烘焙准备"},
    "Transformation And Bounding Box":
        {"zh": "变换和包围盒"},
    "Naming":
        {"zh": "命名"},
    "Modeling":
        {"zh": "建模"},
    "Pivot Align Tube":
        {"zh": "管状模型坐标对齐"},

    # ---- Main menu ----
    "Settings":
        {"zh": "设置"},
    "Switch Layout":
        {"zh": "更换布局"},
    "Language":
        {"zh": "语言"},
    "Switch Language":
        {"zh": "切换语言"},

    # ---- Adv Assistance ----
    "Include Inbetween":
        {"zh": "包含 Inbetween"},
    "Select Children Control":
        {"zh": "选择子控制器"},

    # ---- Bake Preparation
    "Include Material Connection":
        {"zh": "包括材质连接"},
    "Include Children":
        {"zh": "包含子级"},
    "BP_BP_IMC_Btn_Tip":
        {"en": "Copying the nodes linked after the material, currently not supported",
         "zh": "复制材质后面链接的节点，目前不支持" },
    "Unique Selected Material":
        {"zh": "独立选择的材质"},

    # ---- Transform and bbox ----
    "Actual Size":
        {"zh": "实际大小"},
    "TABX_BBSW_ASC_Tip":
        {"en":"The bbox of transform node is the bbox of the transformed shape,\n"
              "which has little practical significance, so it is checked by default",
         "zh": "transform节点的bbox是变换后的shape的bbox的bbox，"
               "基本没有实际意义，所以默认勾选"},
     "Only Selected":
        {"zh": "仅选择"},
    "TABX_BBSW_EXS_Tip":
        {"en": "Exclude children",
         "zh": "不包括子集"},
    "One Large BBox":
        {"zh": "一个大bbox"},
    "TABX_BBSW_OLB_Tip":
        {"en": "all selected objects as a whole",
         "zh": "勾选时将所选所有物体看成一个整体"},
    "Inspect Settings":
        {"en": "Inspect Settings (debug)",
         "zh": "检查（Debug）"},
    "TABX_BBSW_IBS_Btn_Tip":
        {"en": "",
         "zh": "检查数据，debug用"},
    "Check BBox":
        {"zh": "看看你的"},
    "TABX_BBSW_VB_Tip":
        {"en": "Generate a bbox of the selected object",
         "zh": "生成所选取物体的bbox"},
    "Bounding Box Settings:":
        {"zh": "BBox 设置"},
    "Moving:":
        {"zh": "移动："},
    "Exclude Children":
        {"zh": "不包括子级"},
    "TABX_LBBB_MEC_Tip":
        {"en": "When checked, move will not include children",
         "zh": "勾选时移动将不包括子集"},
    "Move To World Center By BBox":
        {"zh": "根据BBox移动到世界中心"},
    "TABX_LBBB_MWCBGB_Tip":
        {"en": "Move to the corresponding position according to the bbox options\n"
               "Pay attention to the selection of only selected and excluded children,\n"
               "Moving when inconsistent may not be as expected\n"
               "When selecting one large bbox, the selected object will move the same distance based on the overall bbox\n"
               "When not checked, each selected object will move according to its own bbox",
         "zh": "根据bbox选项移动到对应位置\n"
               "要注意 仅选择 和 不包括子级 勾选情况，\n"
               "不一致时移动可能并非预想情况\n"
               "勾选 一个大bbox 时所选物体将会根据整体的bbox移动相同的距离\n"
               "不勾选时则每个选择的物体都会根据自己的bbox移动"},
    "Move Pivot By BBox":
        {"zh": "根据BBox移动枢轴"},
    "Keep Pivot Offset":
        {"zh": "保持枢轴偏移"},
    "TABX_LBBB_KPO_Tip":
        {"en":"Maintain the relative position of the pivot to the object after movement\n"
              "Only useful for operations after this option,\n"
              "Generally, the first one is not checked and the second one is checked",
         "zh": "移动后保持枢轴对物体的相对位置，\n"
               "仅对此选项之后的操作有用,\n"
               "一般第一个不勾选，第二个勾选"},
    "Move To Pivot By BBox":
        {"zh": "根据BBox移动到枢轴"},
    "TABX_LBBB_MTPBB_Tip":
        {"en":"Move the object to the pivot position according to the bbox options,\n"
              "Only based on the bbox operation of each object,\n"
              "So one large bbox is useless for this option",
         "zh": "根据bbox选项移动物体到枢轴所在位置，\n"
               "只能根据每个物体的bbox操作，\n"
               "所以one larget bbox对这个选项没用"},
    "Move To World Center By Pivot":
        {"zh": "根据枢轴移至世界中心"},
    "TABX_LBBB_MTWCBP_Tip":
        {"en": "Not related to bbox, move to the world coordinate center based on the pivot position",
         "zh": "和bbox无关，根据枢轴位置移动到世界坐标中心"},

    # ---- Modeling ----
    "Alignment":
        {"zh": "对齐"},
    "Max Trace Length:":
        {"zh": "最大追踪距离："},
    "Point Align Line":
        {"zh": "点对齐线"},
    "M_AW_PAL_Btn_Tip":
        {"en": "Align some points onto a line using only the closest distance\n"
               "The operation is as follows: \n"
               "1. Select some points, where the first two points are the points that determine the line segment\n"
               "The remaining points are the ones that need to be moved\n"
               "2. Alternatively, use multi-component selection, regardless of order, to select the first option\n"
               "The edges are aligned edges, and the other points are the points that need to be used",
         "zh": "将一些点对齐到一条线上，只能使用最近距离\n"
               "操作如下：\n"
               "1.选定一些点，其中前两个点为确定线段的点\n"
               "  其余点为需要移动的点\n"
               "2.或者使用多组件选择，无关顺序，所选的第一条\n"
               "  边为对齐边，其余点为需要用到的点"},
    "Face Align Direction:":
        {"zh": "面对齐方向："},
    "M_AW_FACB_Tip":
        {"en": "",
         "zh": ""},
    "closest":
        {"en": "Closest",
         "zh": "最近"},
    "normal":
        {"en": "Normal",
         "zh": "法线"},
    "Point Align Face":
        {"zh": "点对齐面"},
    "M_AW_PAF_Btn_Tip":
        {"en": "Align some points onto a plane and adjust their position according to the menu above\n"
               "The operation is as follows: \n"
               "1. Select some points, among which the first three points are the points that determine the line segment\n"
               "The remaining points are the ones that need to be moved\n"
               "2. Alternatively, use multi-component selection, regardless of order, to select the first one\n"
               "The face is the alignment plane, and the remaining points are the points that need to be used,",
         "zh": "将一些点对齐到一个平面上，根据上面的选单调整位置\n"
               "操作如下：\n"
               "1.选定一些点，其中前三个点为确定线段的点\n"
               "  其余点为需要移动的点\n"
               "2.或者使用多组件选择，无关顺序，所选的第一个\n"
               "  面为对齐平面，其余点为需要用到的点"},

    "Better Normal":
        {"zh": "更好的法线"},
    "Area Weight":
        {"zh": "面积权重"},
    "Distance Weight":
        {"zh": "距离权重"},
    "Size Scale":
        {"zh": "缩放"},
    "Threshold":
        {"zh": "阈值"},
    "Live Update":
        {"zh": "实时更新"},

    "ReSymmetry Vertices":
        {"zh": "重对称顶点"},
    "Symmetry Plane Position:":
        {"zh": "对称平面位置："},
    "Symmetry Plane Normal:":
        {"zh": "对称平面法线："},
    "M_SV_SSCB_Tip":
        {"en": "Spacial: Select points based on the nearest symmetrical distance\n"
               "Precise: Manually select an even number of points and match which points need to be symmetrical based on the next item\n"
               "         Not recommended for frame selection",
         "zh": "空间：根据对称的最近距离选择点\n"
               "精确：手动选择偶数量的点，根据下一项匹配哪些为需要对称的点，不建议框选"},
    "spacial":
        {"en": "Spacial",
         "zh": "空间"},
    "precise":
        {"en": "Precise",
         "zh": "精确"},
    "Precise Order:":
        {"zh": "精确顺序："},
    "M_SV_POCB_Tip":
        {"en":"First half: The first half of the selected vertices are reference points, and the second half are points that need to be re symmetric\n"
              "Every other: The first of every two points is a reference point, and the second is a resymmetric point",
         "zh": "前一半：选择的顶点中前一半是参照点，后一半是要重新对称的点\n"
               "每隔一个：每两个点中的前一个是参照点，后一个是重新对称的点"},
    "first_half":
        {"en": "First Half",
         "zh": "前一半"},
    "every_other":
        {"en": "Every Other",
         "zh": "每隔一个"},
    "ReSymmetry":
        {"zh": "重新对称"},
    # "":
    #     {"zh": ""},
    # "":
    #     {"en": "",
    #      "zh": ""},

    # ---- Naming ----
    "start from 1":
        {"zh": "从1开始"},
    "N_N_CRC_Tip":
        {"en": "The suffix starts from 1",
         "zh": "后缀从1开始"},
    "Add Serial Number Suffix":
        {"zh": "增加序号后缀"},

    # ---- Pivot Align Tube ----
    "Translation":
        {"zh": "平移"},
    "Orientation":
        {"zh": "朝向"},
    "Automatic bake pivot if more than one":
        {"zh": "当选择大于1时自动烘培枢轴"},
    "PA_BIM_Tip":
        {"en": "If the selected object is greater than 1, bake the pivot, otherwise the result may not be saved",
         "zh": "如果选择的物体大于1就烘焙枢轴，否则结果可能不会保存"},
    "max":
        {"zh": "最大"},
    "min":
        {"zh": "最小"},
    "selected_loop":
        {"en": "selected loop",
         "zh": "选择的循环"},
    "ignore":
        {"en": "ignore",
         "zh": "忽略"},
    "PA_SM_Tip":
        {"en": "Max: Find the hole with the largest area"
               "Min: Find the hole with the smallest area"
               "Selected Loop: Selected Loop Edge"
               "ignore: only transforms the pivot, used for editing the object",
         "zh": "最大：找到面积最大的洞\n"
               "最小：找到面积最小的洞\n"
               "选择的循环：选择的循环边\n"
               "忽略：只变换枢轴，用于编辑物体"},
    "Pivot Axis To Align:":
        {"zh": "要对齐的轴向:"},
    "Align":
        {"zh": "对齐"},
    "Invert Pivot":
        {"zh": "反转枢轴"},
    "PA_IP_Btn_Tip":
        {"en": "Rotate the pivot 180 ° around the axis of the secondary pivot",
         "zh": "绕次级枢轴轴向旋转枢轴180°"},
    "Bake Pivot":
        {"zh": "烘焙枢轴"},
    "Secondary Pivot Axis To Align:":
        {"zh": "次级枢轴对齐轴向"},
    "Secondary Pivot Dir To Align:":
        {"zh": "次级枢轴对齐方向"},
    "world_x":
        {"en": "World X Axis",
         "zh": "世界 X 轴"},
    "world_y":
        {"en": "World Y Axis",
         "zh": "世界 Y 轴"},
    "world_z":
        {"en": "World Z Axis",
         "zh": "世界 Z 轴"},
    "custom_pos":
        {"zh": "自定义位置"},
    "Custom Saved Position:":
        {"zh": "自定义保存位置："},
    "Remember Position":
        {"zh": "记忆位置"},
    "Align Secondary Pivot Axis":
        {"zh": "对齐次级轴向"},
    "Batch All":
        {"zh": "批处理"},
    "PA_AB_Btn_Tip":
        {"en": "align the main and secondary axes at once",
         "zh": "同时对齐主轴和次轴"},
    "Zero Rotation":
        {"zh": "旋转归零"},

    # "":
    #     {"zh": ""},
    # "":
    #     {"en": "",
    #      "zh": ""},
    # "":
    #     {"zh": ""},
    "Repaint":
        {"zh": "重绘"},
}