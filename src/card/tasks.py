from apple.middleware import AppleCard


async def task_update_card(client_id, team_id, pass_id, pass_sn, company_name,
                           top_text_header, top_text_content, text_left_header,
                           text_left_content, text_right_header, text_right_content,
                           color_background, color_text, logo, background, icon_push):
    apple = AppleCard()
    await apple.update_card(
        client_id,
        team_id,
        pass_id,
        pass_sn,
        company_name,
        top_text_header,
        top_text_content,
        text_left_header,
        text_left_content,
        text_right_header,
        text_right_content,
        color_background,
        color_text,
        logo,
        background,
        icon_push
    )


async def task_update_push(client_id, team_id, pass_id, pass_sn, company_name,
                           top_text_header, top_text_content, text_left_header,
                           text_left_content, text_right_header, text_right_content,
                           color_background, color_text, logo, background, icon_push, my_dict):
    apple = AppleCard()
    await apple.update_push(
        client_id,
        team_id,
        pass_id,
        pass_sn,
        company_name,
        top_text_header,
        top_text_content,
        text_left_header,
        text_left_content,
        text_right_header,
        text_right_content,
        color_background,
        color_text,
        logo,
        background,
        icon_push,
        my_dict
    )
