from enum import Enum


class DBTypes:
    class _Base:
        name: str

        @classmethod
        def build(cls, value: str | list[str]) -> str | list[str]:
            if isinstance(value, str):
                return f"{cls.name}('{value}')"
            elif type(value) is list:
                return ','.join([f"{cls.name}('{v}')" for v in value])
            raise RuntimeError()

    class OrderStatus(_Base):
        name = 'order_status'

    class VerificationRequestStatus(_Base):
        name = 'verification_request_status'


class DBTables(str, Enum):
    car_base = 'car_base'
    photos = 'photos'
    private_photos = 'private_photos_info'
    order_file = 'order_file'
    news = 'news'

    courier = 'courier'
    car_info = 'car_info'
    driver_info = 'driver_info'
    person_info = 'person_info'
    agreement_info = 'agreement_info'
    courier_geo = 'courier_geo'

    route_point = 'route_point'
    route_point_security_code = 'route_point_security_code'
    route = 'route'
    order = 'delivery_order'
    order_fully_view = 'order_fully_view'
    order_payments = 'order_payments'

    gmaps_places = 'gmaps_places'

    employee = 'employee'
    customer = 'customer'
    customer_company = 'customer_company'
    legal_company = 'legal_company'
    individual_company = 'individual_company'

    users = 'users'
    preferences = 'preferences'
    notice_receiver = 'notice_receiver'
    notification = 'notification'
    bulk_notification = 'bulk_notification'

    cooperator = 'cooperator'
    verification_request = 'verification_request'
    checkr_check = 'checkr_check'

    twilio_proxy_session = 'twilio_proxy_session'

    coupon = 'coupon'
    employee_coupon = 'employee_coupon'
    invoice = 'invoice'
    faq = 'faq'
    review = 'delivery_review'
    customer_address = 'customer_address'
    customer_lead = 'customer_lead'
    courier_lead = 'courier_lead'
    favorite_point = 'route_point_favorite'
    bonus = 'courier_bonus'

    courier_referral = 'courier_referral'
    courier_referral_payments = 'courier_referral_payments'

    app_zone = 'app_zone'
