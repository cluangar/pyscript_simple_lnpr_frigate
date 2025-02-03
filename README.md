Use on Home Assistant to send event to LNPR API

# Prerequisites
1. Addons pyscript
2. LNPR API: docker pull cluangar/simple_lnpr_frigate

# FlowChart (lnpr_s pyscript)
![FlowChart_lnpr_s_pyscript](https://github.com/user-attachments/assets/391e0711-a39d-4b28-a834-2fef12746956)

# FlowChart (Automation)
![Automation_Call_simple_lnpr_api](https://github.com/user-attachments/assets/9a69c1c3-c8c5-4840-995a-cfbc321f9995)

# FlowChart (LNPR API Docker)
![FlowChart_lnpr_fastapi](https://github.com/user-attachments/assets/e519d7a3-6122-4cae-8f5a-ef43883175d7)

# Running
1. Add pyscript to Hass
2. Add Automation yaml to Hass
3. Install LNPR API Docker

*Recommanded use 2 dual stream resolution from Camera
1. Low Res for Detect (Recommaned minimum 720P or higher for OCR)
2. Righ Res for Record (Recommaned maximum can alternative used for OCR)

![Demo_Simple_LNPR01_Filter](https://github.com/user-attachments/assets/e77500c4-554a-4688-b45d-f46b348943a4)
