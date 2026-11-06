from enum import Enum

class ChatStep(str, Enum):
    PARSE_QUERY = "parse_query"              # Phân tích câu hỏi
    DETECT_INTENT = "detect_intent"          # Xác định mục đích pháp lý
    EXTRACT_SCOPE = "extract_scope"          # Phạm vi áp dụng (loại công trình, đối tượng)
    RETRIEVE_STANDARD = "retrieve_standard"  # Tra cứu QCVN / TCVN
    FILTER_DOCUMENT = "filter_document"      # Lọc điều khoản liên quan
    CROSS_CHECK = "cross_check"               # Đối chiếu, so sánh quy chuẩn
    VALIDATE_COMPLIANCE = "validate"          # Kiểm tra tuân thủ
    SYNTHESIZE_ANSWER = "synthesize"          # Tổng hợp kết luận
    CITE_SOURCE = "cite"                      # Gắn trích dẫn

class ChatEventType(str, Enum):
    STATUS = "status"     # step / progress
    ANSWER = "answer"     # stream token
    DONE = "done"         # kết quả cuối
    ERROR = "error"
