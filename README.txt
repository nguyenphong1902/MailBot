Chạy file main.py sẽ quét những mail UNSEEN và nhập liệu lên trang Pleiger
Chạy file selenium-captcha sẽ demo quá trình vượt qua recaptcha v2 của google
Yêu cầu để chạy đc script:
- Cài đặt Python và pip
- Cài đặt thư viện bằng cách Mở cmd đến thư mục chứa project, gõ: pip install -r requirement.txt
- Nếu chromedriver ko chạy thì phải tải chromedriver mới tương ứng với Google chrome đang dùng 
- Thay đổi địa chỉ hòm mail mong muốn trong file main.py
- Mail đơn hàng có dạng:
###
Dear MES,

I want to order:

Sales Classification: VRC
User Project Code: PR 20210126001
Project Name: Project test 3
In charge: in charge
Plan Delivery Date: 1/27/2021
Product Type: [01.Test-FNItem001] 01.Test-FNItem001
Product: [TESTFNITEM002] TESTFNITEM002
Customer: A.P MOLLER-MAERSK LINE A/S
Order Number: 100
Domestic Foreign: Domestic
Order Quantity: 100
Monetary Unit: Europe-Euro   (EUR)
Order Price: 100
Vat Type: Include
Vat Rate: 1
Exchange Rate: 1
Exchange Rate Date: 1/27/2021
Order Team: Business Manager
ETC:

Thanks!
###