MOCK_LOGO_RESULTS = {
    "microsoft": {
        "success": True,
        "logoUrl": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
        "thumbnailUrl": "https://upload.wikimedia.org/wikipedia/commons/4/44/Microsoft_logo.svg",
        "additionalResults": [
            "https://upload.wikimedia.org/wikipedia/commons/9/96/Microsoft_logo_%282012%29.svg",
            "https://upload.wikimedia.org/wikipedia/commons/2/25/Microsoft_icon.svg",
            "https://logos-world.net/wp-content/uploads/2020/09/Microsoft-Logo-700x394.png",
            "https://1000logos.net/wp-content/uploads/2017/04/Microsoft-logo.jpg"
        ]
    },
    "apple": {
        "success": True,
        "logoUrl": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
        "thumbnailUrl": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
        "additionalResults": [
            "https://upload.wikimedia.org/wikipedia/commons/1/1b/Apple_logo_grey.svg",
            "https://www.apple.com/ac/structured-data/images/knowledge_graph_logo.png",
            "https://1000logos.net/wp-content/uploads/2016/10/Apple-Logo.png",
            "https://logos-world.net/wp-content/uploads/2020/04/Apple-Logo.png"
        ]
    },
    "google": {
        "success": True,
        "logoUrl": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
        "thumbnailUrl": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
        "additionalResults": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/800px-Google_%22G%22_Logo.svg.png",
            "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
            "https://logos-world.net/wp-content/uploads/2020/09/Google-Logo-700x394.png",
            "https://1000logos.net/wp-content/uploads/2016/11/New-Google-Logo.jpg"
        ]
    },
    # Add more companies as needed
}

# Default mock response for companies not specifically defined
DEFAULT_MOCK_LOGO = {
    "success": True,
    "logoUrl": "https://via.placeholder.com/150?text=Company+Logo",
    "thumbnailUrl": "https://via.placeholder.com/150?text=Company+Logo",
    "additionalResults": [
        "https://via.placeholder.com/150/0000FF/FFFFFF?text=Option+1",
        "https://via.placeholder.com/150/FF0000/FFFFFF?text=Option+2",
        "https://via.placeholder.com/150/00FF00/FFFFFF?text=Option+3",
        "https://via.placeholder.com/150/FFFF00/000000?text=Option+4"
    ]
}