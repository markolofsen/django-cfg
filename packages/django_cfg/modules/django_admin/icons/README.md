# Material Icons for Django CFG Unfold

This module provides Material Design Icons integration for Django CFG Unfold admin interface.

## 📊 Statistics

- **Total Icons**: 2234
- **Categories**: 24
- **Auto-generated**: Yes (via `generate_icons.py`)

## 🚀 Usage

### Basic Usage

```python
from django_cfg.modules.django_unfold.icons import Icons

# Use in navigation configuration
navigation_item = {
    "title": "Dashboard",
    "icon": Icons.DASHBOARD,  # IDE autocompletion!
    "link": "/admin/",
}
```

### Category-based Selection

```python
from django_cfg.modules.django_unfold.icons import IconCategories

# Get all navigation-related icons
nav_icons = IconCategories.NAVIGATION

# Get all user-related icons  
user_icons = IconCategories.USERS
```

### Validation

```python
from django_cfg.modules.django_unfold.icons import validate_icon_constant

# Validate icon exists
is_valid = validate_icon_constant(Icons.DASHBOARD)  # True
is_valid = validate_icon_constant("nonexistent")    # False
```

## 🔄 Updating Icons

To update to the latest Material Icons:

```bash
cd /path/to/django-cfg/src/django_cfg/modules/django_unfold/icons/
python generate_icons.py
```

This will:
1. Download the latest Material Icons from Google
2. Generate new `constants.py` with all icons
3. Categorize icons for easy discovery
4. Provide IDE-friendly autocompletion

## 📂 File Structure

```
icons/
├── __init__.py              # Main exports
├── constants.py             # 🤖 Auto-generated icon constants
├── icons.py                 # MaterialIcons class & validation
├── icon_validator.py        # Navigation validation utilities
├── generate_icons.py        # 🔄 Icon generator script
├── example_usage.py         # Usage examples
└── README.md               # This file
```

## 🎯 Available Categories

- **Navigation** (124 icons): add_home, add_home_work, add_home_work, add_to_home_screen, app_settings_alt, ... (+119 more)
- **Users** (54 icons): account_balance, account_balance_wallet, account_box, account_circle, account_tree, ... (+49 more)
- **Documents** (70 icons): article, attach_file, audio_file, contact_page, create_new_folder, ... (+65 more)
- **Communication** (174 icons): 3p, add_call, add_comment, add_ic_call, add_ic_call, ... (+169 more)
- **Ai_Automation** (39 icons): auto_awesome, auto_awesome_mosaic, auto_awesome_motion, auto_delete, auto_fix_high, ... (+34 more)
- **Actions** (124 icons): add, add_a_photo, add_alarm, add_alert, add_box, ... (+119 more)
- **Status** (36 icons): check, check_box, check_box_outline_blank, check_circle, check_circle_outline, ... (+31 more)
- **Media** (82 icons): assistant_photo, audiotrack, bluetooth_audio, broken_image, camera, ... (+77 more)
- **Settings** (26 icons): admin_panel_settings, app_settings_alt, build, build_circle, construction, ... (+21 more)
- **Commerce** (18 icons): attach_money, local_convenience_store, local_grocery_store, money, money_off, ... (+13 more)
- **Travel** (61 icons): car_crash, car_rental, car_repair, card_giftcard, card_membership, ... (+56 more)
- **Social** (214 icons): 18_up_rating, 6_ft_apart, add_moderator, add_reaction, architecture, ... (+209 more)
- **Device** (217 icons): 1x_mobiledata, 30fps, 3g_mobiledata, 4g_mobiledata, 4g_plus_mobiledata, ... (+212 more)
- **Editor** (162 icons): add_chart, add_comment, align_horizontal_center, align_horizontal_center, align_horizontal_left, ... (+157 more)
- **Maps** (228 icons): 360, add_business, add_location, add_location_alt, add_road, ... (+223 more)
- **Notification** (83 icons): account_tree, adb, airline_seat_flat, airline_seat_flat_angled, airline_seat_individual_suite, ... (+78 more)
- **Content** (105 icons): 30fps_select, 60fps_select, add, add_box, add_circle, ... (+100 more)
- **Hardware** (128 icons): adf_scanner, battery_0_bar, battery_1_bar, battery_2_bar, battery_3_bar, ... (+123 more)
- **Image** (286 icons): 10mp, 11mp, 12mp, 13mp, 14mp, ... (+281 more)
- **Av** (125 icons): 10k, 1k, 1k_plus, 2k, 2k_plus, ... (+120 more)
- **Places** (99 icons): ac_unit, airport_shuttle, all_inclusive, apartment, assured_workload, ... (+94 more)
- **File** (54 icons): approval, archive, attach_email, attachment, attachment, ... (+49 more)
- **Toggle** (193 icons): 3d_rotation, airplanemode_off, airplanemode_on, alarm_off, alarm_on, ... (+188 more)
- **Other** (1138 icons): 10k, 10mp, 11mp, 123, 12mp, ... (+1133 more)

## 🛠️ Development

### Adding New Categories

Edit the `category_keywords` in `generate_icons.py`:

```python
category_keywords = {
    'my_category': ['keyword1', 'keyword2', 'keyword3'],
    # ...
}
```

### Custom Icon Validation

```python
from django_cfg.modules.django_unfold.icons import MaterialIcons

# Check if icon exists
if MaterialIcons.is_valid_icon('my_icon'):
    print("Icon exists!")

# Get suggestions for invalid icons
suggestions = MaterialIcons.suggest_similar_icons('invalid_icon')
print(f"Did you mean: {suggestions}")
```

## 📋 Icon Guidelines

1. **Use Constants**: Always use `Icons.CONSTANT_NAME` instead of strings
2. **Validate**: Use validation functions to check icon existence
3. **Categories**: Browse `IconCategories` for organized icon selection
4. **Update Regularly**: Run the generator script to get latest icons

## 🔗 Resources

- [Material Design Icons](https://fonts.google.com/icons)
- [Google Material Icons GitHub](https://github.com/google/material-design-icons)
- [Django Unfold Documentation](https://unfoldadmin.com/)

---

*This file is auto-generated. Last updated: 2025-09-21 01:14:22*
