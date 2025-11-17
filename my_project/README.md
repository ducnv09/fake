# MyProject Crew

Welcome to the MyProject Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/my_project/config/agents.yaml` to define your agents
- Modify `src/my_project/config/tasks.yaml` to define your tasks
- Modify `src/my_project/crew.py` to add your own logic, tools and specific args
- Modify `src/my_project/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the my_project Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The my_project Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the MyProject Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.


tôi muốn tạo 1 website bán sách, đại khái giống tiki nhưng đơn giản hơn

đang gặp vấn đề là Bán hàng offline gặp hạn chế về mặt bằng, tôi định bán lại sách giấy, website có khách hàng mua sách, trang quản trị danh cho quản lý kho, đơn hàng và nhân viên. tính năng gồm tích hợp thanh toán online, quản lý đơn hàng, hệ thống đánh giá sản phẩm, đánh giá sách, giỏ hàng, thanh toán online, theo dõi đơn hàng. nhóm khách hàng là sinh viên, người đi làm, và mọi đối tượng yêu thích sách. những người sử dụng hệ thống là khách hàng, nhân viên, quản lý kho. thanh toán quét mã qr, nội dung qr là tài khoản ngân hàng của tôi



trong trang quản trị, thì theo dõi số lượng từng đầu sách, cảnh báo tồn kho, xuất nhập kho


Về giao hàng, tôi chỉ sử dụng một hình thức duy nhất: khách thanh toán trước, sau đó đơn vị vận chuyển giao đến địa chỉ khách.
Tôi chưa có nhu cầu cho các tùy chọn khác.
Về thanh toán, tôi chỉ hỗ trợ thanh toán online.

công thanh toán là sẽ có hình ảnh mà qr của ngân hàng của tôi, xong mọi người quét vào và thanh toán thôi

hệ thống đánh giá thì khách hàng mua xong được bình luận, đánh giá sao, quản lý sẽ quản lý mấy cái đấy

trang quản trị thì cho quản lý dùng, còn nhân viên thì sẽ có trang riêng, nhân viên sẽ nhập số lượng sách, tạo các loại sách, quản lý sách

nhân viên chỉ được chỉnh sửa thông tin sách hay có thể xóa, cập nhật trạng thái sách

mục tiêu là tăng doanh số, nâng cao trải nghiệm khách hàng

đề xuất giải pháp


đề xuất  
web search
đưa ra lựa chọn

đề xuất Feature, Workflow, Integration

state brief

có login không 2fa, token, 

solution dựa câu hỏi

init = 0
 
hỏi 

recommend

sửa

route

có những case nào

screen, service, flow

Requirements → Product Brief → Solution Design → Epic/Story










BA: "Xin chào! Bạn muốn xây dựng hệ thống gì?"
User: "Tôi muốn bán sách online"

BA: "Tại sao bạn cần hệ thống này? Bạn đang gặp vấn đề gì?"
User: "Tôi bán offline nhưng mặt bằng hạn chế, khó tiếp cận khách hàng xa"

BA: "Ai sẽ sử dụng hệ thống?"
User: "Khách hàng mua sách, nhân viên quản lý kho, quản lý xem báo cáo"

BA: "Bạn muốn có những tính năng gì?"
User: "Giỏ hàng, thanh toán QR code, theo dõi đơn hàng, quản lý tồn kho..."

BA: "Về thanh toán, bạn muốn hỗ trợ những hình thức nào?"
User: "Chỉ thanh toán online bằng QR code thôi, quét vào tài khoản ngân hàng của tôi"

BA: "Về giao hàng thì sao?"
User: "Khách thanh toán trước, sau đó đơn vị vận chuyển giao đến địa chỉ"






 WSJF là gì và tại sao không được sử dụng?

WSJF là phương pháp ưu tiên công việc trong SAFe (Scaled Agile Framework), tính theo công thức:
WSJF = Cost of Delay / Job Duration
Cost of Delay = User-Business Value + Time Criticality + Risk Reduction

Lý do không dùng WSJF ở Product Brief:
- Product Brief là tài liệu định nghĩa WHAT (xây dựng cái gì), không phải HOW (làm thế nào) hay WHEN (làm khi nào)
- WSJF thường được áp dụng ở cấp độ Epic/Feature prioritization trong Backlog, không phải ở Product Brief
- Product Brief tập trung vào vision, problem, goals, còn WSJF tập trung vào prioritization và scheduling


Lean Kanban là phương pháp quản lý công việc dựa trên nguyên tắc "pull system" (kéo công việc) và tối ưu hóa flow.

  Nguyên tắc cốt lõi:

  a) Visualize Work (Trực quan hóa)
  - Dùng bảng Kanban với các cột: To Do → In Progress → Done
  - Mỗi card = 1 Epic/Story

  b) Limit WIP (Giới hạn công việc đang làm)
  - Ví dụ: Chỉ được có tối đa 3 stories ở cột "In Progress"
  - Tránh làm nhiều việc cùng lúc → giảm context switching

  c) Manage Flow (Quản lý luồng công việc)
  - Đo cycle time: thời gian từ khi bắt đầu đến khi hoàn thành
  - Tìm bottleneck (nơi tắc nghẽn)

  d) Continuous Improvement (Cải tiến liên tục)
  - Retrospective thường xuyên
  - Tối ưu process

  e) Explicit Policies (Chính sách rõ ràng)
  - Definition of Ready: Story nào được kéo vào "In Progress"?
  - Definition of Done: Story nào được chuyển sang "Done"?

  Ví dụ bảng Kanban:

  ┌─────────────┬──────────────┬──────────────┬─────────┐
  │  Backlog    │   Ready      │ In Progress  │  Done   │
  │  (sorted    │   (WIP=∞)    │  (WIP=3)     │         │
  │  by WSJF)   │              │              │         │
  ├─────────────┼──────────────┼──────────────┼─────────┤
  │ Story A     │ Story D      │ Story G      │ Story J │
  │ (WSJF=8.5)  │              │ Story H      │ Story K │
  │             │              │ Story I      │         │
  │ Story B     │ Story E      │              │         │
  │ (WSJF=7.2)  │              │              │         │
  │             │              │              │         │
  │ Story C     │ Story F      │              │         │
  │ (WSJF=6.1)  │              │              │         │
  └─────────────┴──────────────┴──────────────┴─────────┘


 WSJF (Weighted Shortest Job First) là công thức toán học để ưu tiên công việc dựa trên giá trị kinh tế.

  Công thức:

  WSJF = Cost of Delay (CoD) / Job Size

  Chi tiết từng thành phần:

  A) Cost of Delay (Giá trị + Sự khẩn cấp) = 3 yếu tố:

  1. User-Business Value (1-10)
    - Giá trị mang lại cho user/business
    - Ví dụ:
        - "Thanh toán QR" = 10 (critical, không có thì không bán được)
      - "Đánh giá sao" = 6 (nice to have, nhưng không critical)
  2. Time Criticality (1-10)
    - Mức độ khẩn cấp theo thời gian
    - Ví dụ:
        - "Login" = 10 (phải có ngay từ MVP)
      - "Xuất báo cáo Excel" = 3 (có thể làm sau)
  3. Risk Reduction / Opportunity Enablement (1-10)
    - Giảm rủi ro kỹ thuật HOẶC mở cơ hội kinh doanh
    - Ví dụ:
        - "Tích hợp API thanh toán" = 9 (rủi ro cao, cần test sớm)
      - "Thêm màu sắc UI" = 2 (ít rủi ro)

  B) Job Size (1-10)
  - Ước lượng effort (story points, days, hours)
  - Ví dụ:
    - 1-2 = XS (vài giờ)
    - 3-5 = S-M (1-3 ngày)
    - 6-8 = L (1 tuần)
    - 9-10 = XL (>1 tuần)

  Ví dụ tính WSJF:

  | Story        | User Value | Time Crit | Risk/Opp | CoD | Job Size | WSJF |
  |--------------|------------|-----------|----------|-----|----------|------|
  | Login        | 10         | 10        | 8        | 28  | 5        | 5.6  |
  | QR Payment   | 10         | 9         | 9        | 28  | 8        | 3.5  |
  | Review sao   | 6          | 4         | 3        | 13  | 3        | 4.3  |
  | Export Excel | 4          | 2         | 2        | 8   | 4        | 2.0  |

  → Thứ tự ưu tiên: Login (5.6) → Review sao (4.3) → QR Payment (3.5) → Export Excel (2.0)


  Job Size = ước lượng xem làm cái này mất bao nhiêu công sức so với những item khác.


 I - Independent (Độc lập) ⚠️
  - Không có field để tracking dependencies giữa các stories
  - Không có mechanism để đảm bảo stories có thể develop độc lập

  N - Negotiable (Có thể thương lượng) ⚠️
  - Không có field priority/importance
  - Không có field status (To Do, In Progress, Done)
  - Không có created_by/updated_by để track conversation với stakeholders

  V - Valuable (Có giá trị) ✅ (Một phần)
  - Title format yêu cầu "so that [benefit]" → thể hiện value
  - Nhưng không có field business_value score

  E - Estimable (Có thể ước lượng) ❌
  - THIẾU story_points/effort estimation
  - THIẾU complexity level

  S - Small (Nhỏ gọn) ⚠️
  - Không có constraint về size
  - Không có field để track nếu story quá lớn cần split

  T - Testable (Có thể kiểm thử) ✅ (Tốt)
  - Có acceptance_criteria field
  - Format Given-When-Then được yêu cầu trong tasks.yaml:56


