# Dynamic Search Extended

**Version:** 18.0.1.0.0
**Author:** TwenTIC
**License:** LGPL-3
**Odoo Version:** 18.0

---

## Overview

*Dynamic Search Extended* allows administrators to add custom text search fields to the search bar of **any Odoo model**, without writing code or XML. Filters are deployed as proper inherited `ir.ui.view` records, so they integrate seamlessly with Odoo's native search mechanism.

---

## Technical Impact on the System

### What the module does to `ir.ui.view`

When the administrator clicks **"Create Search Filters"**, the module:

1. Locates the **primary search view** (`type='search'`, `mode='primary'`) for the selected model.
2. For **each configured line**, creates one `ir.ui.view` record of type `inherit` that inserts a `<field>` node inside the `<search>` element via XPath:

   ```xml
   <data>
     <xpath expr="//search" position="inside">
       <field name="partner_id"
              string="City"
              filter_domain="[('partner_id.city', 'ilike', self)]"/>
     </xpath>
   </data>
   ```

3. Registers a **stable external ID** (`ir.model.data`) with `noupdate=True` for each generated view. This prevents duplicates on re-activation and protects the record from being removed during module upgrades.

The reference to each generated view is stored in `dynamic.search.generator.line.view_id`, enabling clean removal later.

### When "Remove Search Filters" is clicked

The module:

1. Deletes the `ir.ui.view` record linked to each line.
2. Deletes the corresponding `ir.model.data` entry to free the external ID.
3. Clears `view_id` on the line and resets the generator state to **Draft**.

### Key models introduced

| Model | Table | Purpose |
|---|---|---|
| `dynamic.search.generator` | `dynamic_search_generator` | Holds the generator configuration (model + lines). |
| `dynamic.search.generator.line` | `dynamic_search_generator_line` | One row per search field; tracks the generated view. |

### Access rights

| Group | Read | Write | Create | Delete |
|---|---|---|---|---|
| `base.group_system` (Administrator) | ✓ | ✓ | ✓ | ✓ |
| `base.group_user` (Internal user) | ✓ | — | — | — |

---

## Installation

1. Copy the `dynamic_search_extended` folder into your Odoo addons path.
2. Update the apps list: **Settings → Apps → Update Apps List**.
3. Search for *"Dynamic Search Extended"* and click **Install**.

---

## User Manual

### Step 1 – Open the configuration menu

Navigate to **Settings → Technical → Dynamic Search → Search Generators**.

> If the Technical menu is not visible, enable developer mode first:
> *Settings → General Settings → Activate the developer mode*.

---

### Step 2 – Create a new generator

Click **New** to open the generator form.

| Field | Description |
|---|---|
| **Name** | A descriptive identifier for this configuration (e.g. "Sale Order – Partner Filters"). |
| **Model** | The Odoo model you want to extend (e.g. `Sale Order`). |

---

### Step 3 – Add search lines

In the **Search Lines** tab, click **Add a line** for each filter you want to create:

| Column | Description |
|---|---|
| **Label** | The text that will appear in the search bar dropdown (e.g. `Customer City`). |
| **Field Expression** | The field path to filter on. See examples below. |

**Field Expression examples:**

| Expression | Filters on |
|---|---|
| `name` | The record's name field |
| `partner_id.city` | The city of the linked partner |
| `partner_id.country_id.name` | The country name of the linked partner |
| `order_line.product_id.name` | Product names on order lines |
| `bank_ids.acc_number` | Bank account numbers |

> **Rule:** use standard Python dotted-path notation. Each segment must be a valid field technical name. The module validates the format and rejects invalid expressions.

---

### Step 4 – Deploy the filters

Click the **"Create Search Filters"** button in the form header.

- The button is only visible when the generator is in **Draft** state.
- After successful deployment, the state changes to **Active** and the **Deployed** column in each line shows a green checkmark.

---

### Step 5 – Test the filter

Open the model you configured (e.g. go to **Sales → Orders**).
Click the search bar — your new filters appear in the suggestion dropdown with the labels you defined.

---

### Step 6 – Remove the filters

If you want to remove the generated search fields:

1. Open the generator record.
2. Click **"Remove Search Filters"** (only visible in **Active** state).
3. The generated views are deleted from the database and the state returns to **Draft**.

You can then modify the lines and re-deploy.

---

## Notes and Best Practices

- **Dotted paths and relational fields:** when using an expression like `partner_id.city`, the module uses `partner_id` as the `name` attribute of the search `<field>` and `[('partner_id.city', 'ilike', self)]` as the `filter_domain`. This is the standard Odoo pattern for searching through related fields.
- **One view per line:** each line generates its own inherited view. This allows you to remove individual filters without affecting others.
- **External IDs with `noupdate=True`:** generated views are registered with stable external IDs and marked as non-updatable to survive module upgrades.
- **Model locked when active:** once the generator is active, the **Model** field and the **Search Lines** tab become read-only to prevent inconsistent states. Remove the filters first if you need to change the configuration.
- **No restart required:** views are applied immediately upon creation — no Odoo server restart is needed.
