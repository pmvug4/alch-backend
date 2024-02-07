from core.models import FormattedDict

not_developed_error = "This feature hasn't yet been developed."
race_condition_error = "Please try again"

unhandled_exception_text = "Error processing request."
validation_error = "Data processing error in request."
auth_error = "Authorisation Error"
auth_token_expired = "Token expired"
auth_otp_checks_exhausted = "The number of password checks has been exhausted, please request a new one"
auth_otp_incorrect_password = "Incorrect password"
auth_otp_incorrect_phone_number = "Phone number is not supported"
unknown_sms_exception_text = "Unknown error in SMS sending"
unknown_call_exception_text = "Unknown error in CALL sending"
unknown_verification_code_error = "Unknown error in verification code sending"
auth_otp_interval = "Request a password later"
auth_otp_send_fail = "Error sending password, try again later"
auth_otp_forbidden = "Authorization using a one-time password is prohibited"
access_forbidden = "Access is denied"
too_many_entity = "User type registration error"
cant_create_entity = "User type registration error"
unable_to_create_user = "User creation error"
user_name_is_busy = "User with this name is already registered"
user_bulk_creation_unique_index_error = "One or more usernames are busy already registered"
lead_already_exist = "Lead already exist"
customer_entity_not_founded = "The user has not type defined"
stripe_account_create_failed = "Can't create stripe account"
stripe_cant_get_stripe_account_url = "Can't get account url. Try later"
courier_unverified_wait_for_verification = "Wait until you profile will be verified"
courier_does_not_exist = "Driver doesn't exist"

route_does_not_exist = "This route hasn't yet been created."
route_time_or_asap = "Only one of time or asap is required"
route_point_does_not_exist = "Waypoint not defined"
too_many_arrival_points = "Maximum Allowed Delivery Addresses: You have reached the limit of 5 delivery addresses. To add a new address, please delete one of the existing addresses first."
unable_to_get_direction = "It isn't possible to plot a route using these points."
transport_repeat_error = "Google map transport internal error"
route_point_is_unknown = "Waypoint doesn't belong to this route"
route_point_was_already_achieved = "The point has already been reached"

order_draft_does_not_exist = "This draft order hasn't been created yet"
access_to_order_draft_denied = "Access to draft order denied"

unexpected_order_status = "Incorrect order status"
order_does_not_exist = "This order hasn't yet been created."
invalid_is_sender_state = "This order for other person, you cant send verification code"
order_code_overlay_not_exist = "No order code overlay"
access_to_order_denied = "Access to this order is prohibited"
invalid_assigned_courier_id = "The driver assigned to the order is incorrect"
order_departure_time_must_be_changed = "Delivery start time needs to be changed"
defined_price_less_then_calculated = "The specified price is less than the minimum (calculated by the system)"
order_is_already_in_delivery = "Order already in delivery"
order_is_not_in_delivery = "Order not yet delivered"
order_is_already_delivered = "Order already delivered"
order_is_already_published = "Order already published"
order_is_not_published = "Order not published"
order_is_already_unpublished = "The order has already been withdrawn from publication"
order_is_not_unpublished = "The order has not yet been removed from publication"
order_is_already_cancelled = "The order has already been canceled"
order_already_paid = "Order already paid"
another_payment_intent_exist = "This payment is in the process of payment, try again later"
unable_cancel_payment_intent = "Failed to cancel an existing payment attempt, try again later"
payment_common_error = "Having problems with your payment, change your payment method or try again later"
order_cant_be_paid = "Failed to pay, try again later"

notification_access_denied = "Access to this notice is denied"
notification_does_not_exist = "This notice does not exist."
news_does_not_exist = "This news does not exist"
bulk_notification_receiver_ids_dont_match_user_group = "Bulk notification receiver IDs don't match user group"
bulk_notification_does_not_exist = "Bulk notification does not exist"

no_other_payment_method = "No other payment method"
not_valid_payment_method_id = "Invalid payment method id"

you_have_open_orders_exception = "Unable to delete account, you have open orders"

person_info_does_not_exist = "Personal information is not filled"
person_info_already_exists = "Personal information already filled"
driver_info_does_not_exist = "Driver information not yet filled"
driver_info_already_exists = "Driver information already filled"
car_info_does_not_exist = "Car information not yet filled"
car_info_already_exists = "Car information already filled"
car_info_with_this_number_already_exists = "The car with the given number already exists"

no_geolocation_error = "You need to provide geolocation"
order_contract_cant_be_rejected = "You cannot reject a custom contract"

wrong_order_verify_code = "Invalid order verification code"

courier_charges_disabled_error = "The driver has no payment set up"

route_cant_be_finished = "The order could not be completed (there are points not reached)."

photo_does_not_exist = "Photo not found"
photo_not_in_list = "Photo not exist in your photos"
file_does_not_exist = "File not found"
review_is_not_exist = "Review is not exist"
review_already_exist = "Review already exist"
unknown_courier_review_dashboard = "Unknown Courier Review Dashboard"
file_size_too_big = "File size too big"
disallowed_file_extension = "Allowed only .PDF, .DOC, .DOCX extensions"
private_photo_info_does_not_exist = "Private photo info not found"

company_does_not_exist = "Company not defined"
address_is_not_exist = "Address is not exist"
favorite_point_not_exist = "Favorite point does not exist"
favorite_point_access_denied = "Favorite point access denied"

customer_does_not_exist = "customer does not exist"
customer_already_exists = "The customer already exists"

employee_does_not_exist = "Employee does not exist"
employee_already_exists = "Employee already exists"
employee_phone_is_busy = "Employee phone is busy"

unprocessable_customer_update_form = "Perhaps you are trying to transfer company when updating an individual."

manager_not_founded = "Manager not found"

wrong_courier_car_body = "You cannot accept this order with your car body"
courier_avatar_does_not_exist = "The driver does not have an avatar"
courier_is_locked_for_editing_error = "Driver locked for editing. " \
                                      "(Or a verification request has been sent, or there are active orders)"
courier_is_unfilled = "Driver is unfilled"
courier_redeem_referral_error = "You cannot use a referral code because you have already completed at least 1 order"
courier_receive_referral_error = 'It is impossible to receive a referral code because at least 1 order has not been completed'
referral_transfer_creation_error = 'referral transfer creation error'
courier_referral_does_not_exist = "Courier referral does not exist"
courier_referral_code_does_not_exist = "This referral code does not exist"
courier_referral_code_already_redeemed = 'You have already used the referral code'
courier_verification_already_in_process = "The request for verification has already been sent, please wait."
courier_verification_already_completed = "Driver is already verified"
courier_verification_status_is_incorrect = "Update information"
courier_not_receiving_orders = "You can't search orders when \"Not working\" mode is set, switch to \"Receive orders\""

unexpected_photo_extension = "Wrong photo format"
unexpected_pdf_extension = "PDF unknown error"
unexpected_smtp_extension = "Unknown SMTP error"

route_point_security_code_does_not_generated = "Issuing point verification code not yet generated"
need_regenerate_route_point_security_code = "Verification code of the point of issue must be regenerated"
too_early_to_regenerate_point_security_code = "Too early to regenerate code. " \
                                              "Please wait and try again in a couple of minutes"
route_point_send_code_error = "Error sending point verification code (perhaps the point is not intended for this)"

cooperator_does_not_exist = "Qwqer-employee not defined"

verification_request_does_not_exist = "Application for driver verification not found"
verification_request_wrong_status = "Verification request in wrong status"
verification_request_equals_with_previous = (
    "Sorry, but you cannot resubmit identical requests. "
    "To continue, you will need to modify your request details. "
    "If you encounter any issues or have any questions, you can reach out to our support team."
)
cant_solve_unfamiliar_request = "You cannot resolve someone else's application"

order_cargo_type_changing_denied = "You cannot change the cargo_type of an order"
order_must_be_edited = "Order must be edited"

unknown_courier_order_dashboard_error = "Unknown order dashboard error"
unknown_courier_bonus_dashboard_error = "Unknown bonus dashboard error"
unknown_courier_verification_dashboard_error = "Unknown verification dashboard error"


class CustomerNotifications:
    route_achieved = FormattedDict({
        'title': "Drop off successful!",
        'subtitle': "The driver's successfully delivered your order to {recipient} at {address}. ",
        'description': None
    })
    published = FormattedDict({
        'title': "New Delivery Request Published",
        'subtitle': "Your delivery request for Order #{order_id} has been published. "
                    "A driver partner will be assigned soon.",
        'description': None
    })

    contract_rejected = FormattedDict({
        'title': "Unfortunately, the driver canceled your order.",
        'subtitle': "Your order has been moved to drafts, you can re-order. (Order #{order_id})",
        'description': None
    })

    courier_assigned = FormattedDict({
        'title': "Order Accepted!",
        'subtitle': "A driver partner is on their way to pickup Order #{order_id}",
        'description': None
    })

    courier_arrived = FormattedDict({
        'title': "Driver here!",
        'subtitle': "A driver partner is waiting you to pickup Order #{order_id}.",
        'description': None
    })

    in_delivery = FormattedDict({
        'title': "Delivery in Progress.",
        'subtitle': "Order #{order_id} is now on its way to be delivered.",
        'description': None
    })

    delivered = FormattedDict({
        'title': "Delivery Completed Successfully.",
        'subtitle': "Order #{order_id} has been successfully delivered. Thank you for choosing our service.",
        'description': None
    })

    courier_dropped = FormattedDict({
        'title': "Driver cancelled order #{order_id}.",
        'subtitle': "Uh oh, looks like your driver cancelled this order, don’t worry though, we are already looking for another driver.",
        'description': None
    })

    overdue = FormattedDict({
        'title': "Pickup time expired",
        'subtitle': 'Looks like the pickup time for your order expired before a courier could pick it up. Your order #{order_id} has been moved to "Drafts". If you still need to send the package, we recommend posting your order again.',
        'description': None
    })


class CustomerSMS:
    accepted = FormattedDict({
        'msg': 'Good news {name}! We\'ve found the right driver for your order "{title}"! The driver will arrive at the pickup location as scheduled. Please make sure your items are ready for pickup. Qwqer team.'
    })
    delivered = FormattedDict({
        'msg': 'Hey {name}, your order "{title}" has been successfully delivered. If you have questions or need immediate assistance please contact us via chat. Qwqer team.'
    })
    overdue = FormattedDict({
        'msg': 'Looks like the pickup time for your order expired before a courier could pick it up. Your order "{order_id}" has been moved to "Drafts". If you still need to send the package, we recommend posting your order again.'
    })

    class OtherPerson:
        accepted = FormattedDict({
            'msg': """We are pleased to inform you that a courier has been assigned to pick up your parcel.
Expected time for parcel pickup: {date}
Pick-up address: {address}
Driver: {fullname}
Car: {car_name}
Phone number: {phone}

Please ensure that someone is on site to receive the package at the specified date and time. If you have any questions or need to change your delivery date or time, please contact our customer service department by phone or email: +1 (213) 592-1829 help@qwqer.com
For business partnerships, you can download the partnership application from this link: https://business.qwqer.com
QWQER Team"""})


class CouponCondition:
    lower_bound = FormattedDict({
        'msg': 'Promo code is valid for orders over ${price} only'
    })


class CourierNotifications:
    verification_code = FormattedDict({
        'title': "The sender sent a verification code.",
        'subtitle': "To start delivery tell this code {password} to sender. (Order #{order_id})",
        'description': None
    })

    courier_verification_approved = FormattedDict({
        'title': "Your account was approved!",
        'subtitle': "Congratulations with account approving! Now you can deliver orders.",
        'description': None
    })

    courier_consent_docs_is_ready = FormattedDict({
        'title': "Consent Documents Ready",
        'subtitle': "Check \"Personal Information\" to view your signed Driver's Rules and Regulations Consent.",
        'description': None
    })

    courier_verification_declined = FormattedDict({
        'title': "Sorry, your account hasn't been verified.",
        'subtitle': "Administration declined your request. Reason: \"{request_description}\"",
        'description': None
    })

    new_order_avail = FormattedDict({
        'title': "New contract received!",
        'subtitle': "You have a new contract for delivery. Check the driver app for details and to confirm the order.",
        'description': None
    })

    new_order_avail_all = FormattedDict({
        'title': "New Order Available near you",
        'subtitle': "Click to View Available Orders",
        'description': None
    })

    courier_assigned = FormattedDict({
        'title': "Order Accepted",
        'subtitle': "You can now ride to the pickup location for Order #{order_id}.",
        'description': None
    })

    courier_arrived = FormattedDict({
        'title': "Departure point reached",
        'subtitle': "You can pick up the order from the sender for Order #{order_id}.",
        'description': None
    })

    in_delivery = FormattedDict({
        'title': "Delivery in progress",
        'subtitle': "Order #{order_id} is now Ready to be Delivered.",
        'description': None
    })

    delivered = FormattedDict({
        'title': "Delivery Completed Successfully",
        'subtitle': "Order #{order_id} has been successfully delivered. Thank you for being a valuable partner.",
        'description': None
    })
    sender_courier = FormattedDict({
        'title': "Congratulations ! Someone used your referral code.",
        'subtitle': "You should receive your reward soon.",
        'description': None
    })
    recipient_courier = FormattedDict({
        'title': "Success! Referral conditions are met!",
        'subtitle': "You should receive your reward soon.",
        'description': None
    })
    new_contract = FormattedDict({
        'title': "You have received a new order contract!",
        'subtitle': "The customer has offered you a contract to order!",
        'description': None
    })

    canceled_by_customer = FormattedDict({
        'title': "The customer has cancelled their order.",
        'subtitle': "Heads up! The customer has cancelled their order #{order_id}. No need to proceed with delivery.",
        'description': None
    })

    canceled_by_cooperator = FormattedDict({
        'title': "Admin cancelled order #{order_id}.",
        'subtitle': "Your order has been cancelled by an admin. Write to support services for more info.",
        'description': None
    })

    canceled_by_courier = FormattedDict({
        'title': "Order cancelled by driver.",
        'subtitle': "You cancelled the order #{order_id}, and can no longer make the delivery. It’s now available to other drivers.",
        'description': None
    })

    confirmed = FormattedDict({
        'title': "Success! Your delivery is now confirmed.",
        'subtitle': "The customer has confirmed your order #{order_id}. Congratulations on finalizing your delivery!",
        'description': None
    })


you_need_to_deliver_previous_point_last = "First you must complete the delivery at the previous points."
route_points_must_be_achieved = "The point must be reached."
route_not_enough_proof_of_delivery = "Not enough evidence to complete route."

cant_calculate_order_pay_price = "The expected cost of payment cannot be calculated (there is not enough data)."

no_route_point_security_code = "Point passcode must be provided."
wrong_route_point_security_code = "Wrong passcode for point."

phone_proxy_session_does_not_exist = "There is no proxied phone session"
companion_phone_is_unknown = "The caller didn't provide a phone number"
route_point_no_phone_error = "Recipient phone number not specified"
unable_to_create_proxy_session = "Unable to create proxy session (The companion may have entered the wrong phone number) "
inadmissible_departure_point_phone = "You cannot use your number when 'pick up the parcel'"

incorrect_courier_order = "This courier does not have the specified order"
bonus_is_not_active = "The bonus has already been used or disabled."
bonus_state_cant_be_toggled = "Cant toggle used bonus"
bonus_transfer_creation_error = "Failed to use bonus, please try again later"
bonus_does_not_exist = "Bonus doesn't exist"
coupon_does_not_exist = "Coupon doesn't exist"
coupon_with_this_code_already_exists = "Coupon with this code already exists"
employee_coupon_is_unknown = "Missing coupon information from user side"
employee_coupon_is_already_registered = "The coupon you are attempting to activate has already been redeemed. If you have any questions or need assistance, feel free to contact our support team. Thank you for using our app!"
coupon_is_already_used = "Coupon already used"
coupon_conditions_denied = "Coupon terms not met"
coupon_is_overdue = "Coupon expired"
coupon_is_not_active = "Coupon not active"
invoice_is_unknown = "Missing invoice information from user side"
datetime_timezone_error = "Times must be with tzinfo or Tzinfos must be the same"
faq_is_not_exist = "Faq is not exist"
faq_access_denied = "Faq access denied"
wrong_signature_photo_amount = "wrong signature photo amount for agreement"
unfilled_courier_name = "Please, fill name"
old_signature_photo_amount = "Please update app, documents signing able only in latest version"
agreement_info_does_not_exist = "Agreement information not yet filled"
invalid_agreements = "Signed agreements texts are invalid"
agreement_creation_in_process = "Agreement creation in process, please wait. Casually, it takes less than 1 minute"

agreement_contract_content = ["""As a Driver for QWQER Services, LLC (“QWQER”), I hereby agree and consent to the following rules and regulations:

**A.** I agree to comply with all standards and procedures set forth by QWQER, either as communicated to me directly or as contained in the QWQER Company Policies which I hereby acknowledge I have reviewed, read and comprehend in their entirety. I acknowledge and accepts that adoption of QWQER corporate policies is a precondition to my accepting and performing and Deliveries on behalf of QWQER Customers and that any act I commit in contravention of QWQER policies shall operate as immediate grounds for suspension or permanent ban to Site services.

**B.** As a Driver performing Delivery services for the benefit of QWQER Customers, I further hereby agree and consent to:

**a.** Exercise due care and caution in operation of the delivery vehicle which shall include my strict compliance with all rules as set forth by the California Department of Motor Vehicles (“DMV”). Due care in operation of the delivery vehicle shall mean, but shall not be limited to, obeying all speed limits and operating vehicle in compliance with all applicable directional signs and parking regulations;

**b.** Under no circumstance may I operate the delivery vehicle while under the influence of drugs or alcohol or when my physical or mental condition may otherwise be impaired.

**c.** With respect to the vehicle I use for delivery services, I shall: i.Not use the vehicle for personal errands while going to, during, or returning from a delivery, unless so directed by Employer; ii. Keep the delivery vehicle in good condition and repair; iii.Comply with all rules and regulations governing safe and lawful operation of a motor vehicle; and iv. Comply with such further guidelines as QWQER or the Customer may require, as permitted by law.

**C.** Driver/Courier Warranties. As a Driver performing Delivery services for the benefit of QWQER Customers, I further hereby agree and consent to:
**a.** Upload to the Site a true and correct copy of my DMV report. I agree to provide updated DMV reports upon request and will immediately notify QWQER if I am
involved in any accidents or receive any subsequent citations while performing services through the Site.
**b.** I understand that any violation of the rules and regulations set forth herein or of any of the standards, procedures or guidelines applicable to my Driver services may result in immediate suspension or permanent ban to the Site. In particular, I acknowledge the need for utmost safety and due care in the operation of my delivery vehicle and in the conduct of Delivery services.
**c.** I understand and I am prohibited from carrying any passengers during a Delivery without Customer authorization.
**d.** I agree to only operate the vehicle approved by QWQER and will not drive a
substitute vehicle without QWQER’s prior approval.
**e.** I agree to maintain my automobile insurance (including coverage for bodily injury, property damage and personal liability) at all times while using my vehicle for Delivery services and will inform QWQER if my insurance coverage is changed,
cancelled or terminated.
**f.** I understand that my insurance carrier is solely responsible if I am involved in an accident that causes injury or damage to another person and/or their property. I am also aware that QWQER’s insurance does not cover my vehicle for comprehensive or collision coverage.

All capitalized terms shall have the meanings set forth in the [QWQER User Agreement.](https://qwqer.com/wp-content/uploads/2021/12/QWQER-SITE-User-Agreement.pdf)""",
                              """I hereby attest that holding a valid Driver’s License (“DL”) issued by the California Department of Motor Vehicles (“DMV”) is a precondition to my completing Deliveries as a Driver for the benefit of QWQER Customers and/or other third parties requiring Delivery services. I hereby attest that I do indeed possess the required DL and that my DL is current and in good standing with the State of California, a copy of such DL has been uploaded to the Site and/or is available immediately upon request.""",
                              """I hereby further attest that, in the event my DL is either suspended or revoked, or if I otherwise become incapable, either physically or by law, to drive a motor vehicle within the state of California, that I shall immediately remove myself from consideration for all Deliveries unless/until such time that the conditions causing my inability to perform Delivery services has been removed.""",
                              """I hereby further attest to keep QWQER updated as to all changes that may impact my ability to provide Delivery services, including providing immediate notice to QWQER of any existing or new marks on my DMV driver record, including citations, judgments, and/or any other marks that would be reasonably likely to impact my ability to perform Delivery services as contemplated herein and pursuant to this Agreement and throughout the Site.""",
                              """I agree to provide all available records evidencing my ability to perform Delivery services as requested, either by QWQER, the Customer, or any other third party, and agree that failure to provide requested records is grounds for my removal and permanent ban from Site services.""",
                              """I agree to comply with all QWQER Driver’s Rules and Regulations contained in the [Driver’s Rules and Regulations Consent Form](https://qwqer.com/driver-rules-and-regulations/) or elsewhere in the Site where such rules are governed.""",
                              """I further agree to indemnify and hold QWQER and each of its Affiliates completely harmless in the event that I, without notice to QWQER, fail to comply with the attestations set forth herein or if I otherwise perform Delivery services in contravention of QWQER rules and regulations.""",
                              """All capitalized terms shall have the meanings set forth in the [QWQER User Agreement.](https://qwqer.com/wp-content/uploads/2021/12/QWQER-SITE-User-Agreement.pdf)""",
                              """I,   
                              hereby authorize QWQER Services LLC., and its designated agents and representatives to
conduct a comprehensive review of my background through a consumer report and/or an
investigative consumer report to be generated as a part of their screening process.
I understand that this background check will be used solely for purposes related to evaluating my
suitability for employment, engagement, or any other lawful purpose as deemed necessary by
QWQER Services LLC. I understand that the scope of the consumer report/investigative
consumer report may include, but is not limited to, the following areas:
• Verification of social security number;
• Current previous residences;
• Criminal history, including in-state and out-of-state criminal history records;
• Driving records;
• Any other public records.
I, the undersigned, authorize the procurement of the consumer report and/or investigative
consumer report by QWQER Services LLC. According to the Fair Credit Reporting Act
(FCRA), I am entitled to know if employment is denied because of information obtained by my
prospective employer from a Consumer Reporting Agency. If so, I will be notified and given the
name and address of the agency or the source which provided the information.
I hereby release QWQER Services LLC and its agents, officials, representatives, or assigned
agencies, including officers, employees, or related personnel, both individually and collectively,
from any and all liability for damages of whatever kind, which may at any time result to me, my
heirs, family, or associates because of compliance with this authorization and request to release.
I acknowledge that this consent form will remain on file and shall serve as ongoing authorization
for QWQER Services LLC to procure consumer reports and/or investigative consumer reports at
any time during my employment, engagement, or contract period."""]

failed_to_create_checkr_candidate = "Failed to create/update checkr candidate. Maybe this candidate already exists in checkr."
checkr_check_not_found = "Checkr check not found"
checkr_checking_is_already_started = "Checkr checking is already started"
checkr_unsupported_courier_information = "The driver information for 'checkr' is unsupported. (wrong / unfilled / created using outdated app)"
too_early_for_checkr_check = "Please wait before sending a new 'checkr' request"
checkr_report_not_yet_generated = "Checkr report not yet generated"
checkr_report_not_found = "Checkr report not found"

need_client_phone_error = "You need to set the pick up point phone to create an order."
b2c_order_client_phone_is_busy = "Your phone is already registered. Please create an order using your account."

app_zone_does_not_exist = "Application zone not found."
app_zone_unique_name_error = "Application zone with this name is(-was) already exists(-ed). AppZone name should be unique."
unsupported_order_app_zone = "You cannot accept this order. Cuz it's located in a different application zone."
cant_delete_basic_app_zone = "You cannot delete a primary application zone."
cant_edit_basic_app_zone = "You cannot edit a primary application zone"
app_zone_is_expired = "Your access is expired. Please contact support for more details. "
