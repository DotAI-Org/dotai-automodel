# Data Points Available to Sales Heads — By Vertical

What data does each vertical's sales/distribution head have access to? This determines what features a churn model can use.

---

## Data Type Framework

Companies can be classified not just by industry vertical, but by **what type of data exists alongside transactions**. This determines product scope and feature engineering.

### Type 1: Transaction-only
Just purchase records. Churn = declining recency/frequency/monetary.

| Vertical | Companies | Data |
|----------|-----------|------|
| FMCG distributors | HUL, ITC, Nestle, Britannia, Dabur, Marico, Godrej | Retailer purchase orders: customer_id, date, SKU, quantity, amount |
| Wholesale/B2B suppliers | Steel distributors, chemical traders, electrical wholesalers | Order history from buyers |
| General retail | Reliance Retail, DMart, Spencer's | Customer purchase logs |
| Dairy | Amul, Mother Dairy, Hatsun, Heritage | Daily lifting data: volume, SKU, date |
| Telecom distribution | Jio, Airtel, Vi retailers | Recharge txns, SIM activations |
| Textiles/Apparel wholesale | Raymond, Arvind, Page Industries | Franchisee/MBO orders |
| Footwear wholesale | Bata, Relaxo, Metro Brands | Dealer orders by style/size |

### Type 2: Transaction + service records
Purchase data plus post-sale service/maintenance interactions.

| Vertical | Companies | Additional data beyond txns |
|----------|-----------|---------------------------|
| Auto dealers (OEM) | Maruti, Tata, Mahindra, Hero, Bajaj | Service visits, warranty claims, parts sold, CSI scores |
| Consumer durables | Voltas, Blue Star, Whirlpool, V-Guard | Installation data, service calls, warranty registrations |
| Tyres (fleet) | MRF, Apollo, CEAT | Warranty claims, retread vs new, replacement cycle |
| Batteries | Exide, Amara Raja | Old battery returns (exchange), warranty claims |
| Equipment sellers | Thermax, Cummins, Siemens | Maintenance contracts, repair calls, AMC renewal |

### Type 3: Transaction + loyalty/membership
Purchase data plus engagement in a structured loyalty or membership program.

| Vertical | Companies | Additional data beyond txns |
|----------|-----------|---------------------------|
| Paints (painter programs) | Asian Paints, Berger, Kansai Nerolac | Painter points earned/redeemed, tier, training attendance |
| Cement (mason programs) | UltraTech, Ambuja, ACC, Dalmia | Mason loyalty points, workshop attendance, referrals |
| Wires/cables (electrician programs) | Polycab, Havells, KEI, Finolex | Electrician loyalty points, certifications |
| Lubricants (mechanic programs) | Castrol, Gulf Oil, Veedol | Mechanic points, redemption patterns |
| Tyres (mechanic programs) | MRF, Apollo, CEAT | Mechanic recommendation tracking |
| Auto aftermarket | Bosch, Schaeffler, Minda | Counter staff incentive redemption |

### Type 4: Transaction + delivery/returns
Purchase data plus logistics, returns, and fulfillment data.

| Vertical | Companies | Additional data beyond txns |
|----------|-----------|---------------------------|
| Dairy (perishable) | Amul, Hatsun, Heritage | Daily delivery, spoilage returns, route data |
| D2C physical brands | Mamaearth, Wow Skin, Lenskart, boAt | Orders, shipping, returns, complaints, refunds |
| Subscription boxes | FreshMenu, Licious, Country Delight | Order frequency, skip/pause, cancellation |
| Pharma (stockist) | Sun Pharma, Cipla, Mankind, Abbott | Expiry returns, near-expiry stock, damaged goods |
| Tiles/sanitaryware | Kajaria, Cera, Somany | Breakage returns, size mismatches |
| Textiles/apparel (retail) | ABFRL, Page Industries | Sell-through rates, unsold returns |

### Type 5: Transaction + field interaction
Purchase data plus sales rep visit/call/engagement logs.

| Vertical | Companies | Additional data beyond txns |
|----------|-----------|---------------------------|
| Adhesives (carpenter engagement) | Pidilite, Sika, Henkel (Jivanjor) | Influencer purchases at SKU level, training attendance, medical camps |
| Pharma (doctor engagement) | Sun Pharma, Cipla, Mankind, Torrent | MR call reports, doctor Rx data, sample distribution |
| Agri inputs | UPL, Coromandel, PI Industries, Rallis, Dhanuka | Field officer visits, demo plot results, crop data, seasonal patterns |
| FMCG (with field force) | HUL, ITC, Nestle | Beat plan data, retailer visit frequency, order booking by rep |
| Cement (with field force) | UltraTech, Ambuja | Mason meets, contractor visits, site visits |

### Overlap

Many companies fall into multiple types. Examples:
- **Pidilite** = Type 1 (dealer txns) + Type 3 (carpenter loyalty) + Type 5 (field training)
- **Asian Paints** = Type 1 (dealer txns) + Type 3 (painter loyalty) + Type 5 (tinting machine data)
- **Maruti** = Type 1 (vehicle dispatch) + Type 2 (service records) + Type 3 (dealer incentives)
- **Sun Pharma** = Type 1 (stockist orders) + Type 4 (expiry returns) + Type 5 (MR-doctor calls)

### Product Implication

| Type | Churn Tool Support Today | Gap |
|------|------------------------|-----|
| Type 1 (txn-only) | Supported | None — this is the current product |
| Type 2 (txn + service) | Not supported | Accept service CSVs as second file, join on customer_id |
| Type 3 (txn + loyalty) | Not supported | Accept loyalty/points CSV, use engagement features |
| Type 4 (txn + returns) | Not supported | Accept returns CSV, compute return rate features |
| Type 5 (txn + field) | Partially supported (JACPL has engagements table) | Generalize engagement ingestion |

---

## Per-Vertical Detail

Below is the per-vertical breakdown of data points available to each sales head.

---

## 1. FMCG / Packaged Goods (HUL, ITC, Nestle, Britannia, Dabur, Marico)

**Who churns:** Retailers, distributors, kirana stores

| Data Point | Description |
|------------|-------------|
| Dealer/retailer purchase orders | SKU, quantity, amount, date |
| Order frequency | Weekly/fortnightly ordering cycles |
| SKU mix | Which categories the retailer stocks |
| Credit outstanding | How much the retailer owes |
| Scheme/discount utilization | Whether trade promotions are redeemed |
| Returns/damages | Products returned or marked damaged |
| Beat plan coverage | Salesman visit frequency per retailer |
| Retailer tier/classification | Gold/Silver/Bronze based on volume |
| Secondary sales (some) | Sell-out data from POS if available |

**What they do NOT have:** End-consumer purchase data (except D2C channels).

---

## 2. Dairy (Amul, Mother Dairy, Hatsun, Heritage)

**Who churns:** Parlour owners, retailers, institutional buyers

| Data Point | Description |
|------------|-------------|
| Daily/weekly lifting | Volume of milk, curd, ice cream lifted |
| SKU-level orders | Product mix (pouch milk vs value-added) |
| Payment cycle | Cash vs credit, outstanding days |
| Seasonal patterns | Summer ice cream spikes, winter dips |
| Returns/spoilage | Perishable goods returned |
| Route delivery data | Which route, delivery boy, time |
| Chiller placement | Whether company chiller is placed at retailer |

**Unique:** Perishable goods = daily ordering. Missed days are strong churn signals.

---

## 3. Paints (Asian Paints, Berger, Kansai Nerolac)

**Who churns:** Dealers, painters (influencers)

| Data Point | Description |
|------------|-------------|
| Dealer purchase orders | SKU, quantity, amount, date |
| Tinting machine data | Colors mixed at dealer point — indicates end-customer demand |
| Painter loyalty program | Points earned, redeemed, tier |
| Painter training attendance | Skill workshops, certifications |
| Scheme redemption | Seasonal offers taken up |
| Dealer credit | Outstanding, payment delays |
| Color consultation leads | Leads generated via apps/stores |

**Unique:** Painters are influencers who recommend brands to homeowners. Their engagement data (training, points, app usage) predicts dealer volume.

---

## 4. Adhesives & Construction Chemicals (Pidilite, Sika)

**Who churns:** Dealers, carpenters (influencers), plumbers, masons, contractors

| Data Point | Description |
|------------|-------------|
| Dealer purchase orders | SKU, quantity, amount, date |
| Influencer (carpenter/plumber) purchases | SKU-level tracking via dealer |
| Influencer loyalty program | Points, rewards, redemption |
| Skill training attendance | Workshops, medical camps, certifications |
| Contractor project data | Project size, products recommended |
| Dealer scheme utilization | Volume targets, bonus schemes |
| Product category mix | Adhesives vs waterproofing vs tile grout |

**Unique:** Pidilite tracks 680,000+ outlets AND the carpenters/plumbers who influence purchases. Jivanjor (Henkel) tracks similar carpenter-level SKU purchases through 6,000+ dealers.

---

## 5. Building Materials — Tiles, Sanitaryware, Pipes (Kajaria, Cera, Astral, Supreme)

**Who churns:** Dealers, architects (influencers), plumbers (for pipes)

| Data Point | Description |
|------------|-------------|
| Dealer orders | SKU, quantity, amount, date |
| Product category | Tiles vs sanitaryware vs faucets |
| Architect/designer recommendations | Tracked via influencer programs |
| Display/showroom investment | Whether dealer has brand display |
| Project orders | Bulk orders for construction projects |
| Returns/breakage | High in tiles, tracked by SKU |
| Credit terms | Payment outstanding, tenure |

**Unique:** Architects and interior designers are the primary influencers. Their referral data is tracked.

---

## 6. Cement (UltraTech, Ambuja, ACC, Shree Cement)

**Who churns:** Dealers, masons (influencers), contractors

| Data Point | Description |
|------------|-------------|
| Dealer dispatch data | Volume (bags/MT), date, location |
| Mason loyalty program | Points, rewards, tier |
| Mason training/meets | Attendance at technical workshops |
| Contractor order patterns | Project-linked bulk purchases |
| Credit and payment | Outstanding amount, days |
| Seasonal patterns | Construction season peaks |
| Competitor share at dealer | Whether dealer stocks multiple brands |

**Unique:** Masons recommend cement brands to homebuilders. Mason engagement programs are the churn lever.

---

## 7. Wires, Cables & Electricals (Polycab, Havells, KEI, Finolex, Crompton)

**Who churns:** Dealers, electricians (influencers)

| Data Point | Description |
|------------|-------------|
| Dealer orders | SKU, quantity, amount, date |
| Electrician loyalty program | Points, redemptions |
| Product mix | Wires vs switches vs fans vs lights |
| Project-based orders | Bulk for buildings/factories |
| Electrician training | Certifications, workshops |
| Warranty claims | Defects, replacements |
| Display/branding at dealer | Counter branding, standees |

**Unique:** Electricians recommend wire brands. Their loyalty data predicts dealer volumes.

---

## 8. Steel Pipes (APL Apollo, Jindal SAW)

**Who churns:** Dealers, fabricators, contractors

| Data Point | Description |
|------------|-------------|
| Dealer orders | Product type, tonnage, date |
| Fabricator purchases | Tracked via dealer |
| Project pipeline | Construction/infra project orders |
| Price sensitivity | Response to price changes |
| Credit utilization | Outstanding, payment frequency |
| Competitor stocking | Dealer stocking rival brands |

**Unique:** Commodity product — price and credit terms drive loyalty more than brand. Fabricators are the influencers.

---

## 9. Consumer Durables & Appliances (Voltas, Blue Star, Whirlpool, V-Guard, TTK Prestige)

**Who churns:** Dealers, retailers

| Data Point | Description |
|------------|-------------|
| Dealer sell-in | Units, models, amount, date |
| Dealer sell-out (some) | End-consumer sales data |
| Warranty registrations | End-customer activations |
| Service calls | Post-sale service requests |
| Installation data | For ACs, water purifiers — install completion |
| Seasonal patterns | Summer for ACs, winter for heaters |
| Display models | Brand counter share at multi-brand outlets |
| Scheme and incentive | Target-based dealer bonuses |

**Unique:** Warranty registration = proxy for sell-through. Service call frequency = product quality signal.

---

## 10. Tyres (MRF, Apollo, CEAT, JK)

**Who churns:** Dealers, fleet operators, mechanics (influencers)

| Data Point | Description |
|------------|-------------|
| Dealer orders | Size, type (car/truck/bike), quantity, date |
| Fleet operator purchases | Tracked via dedicated reps |
| Mechanic recommendations | Loyalty programs for mechanics |
| Retread vs new | Replacement patterns |
| Warranty claims | Defect-based returns |
| OEM vs replacement | Channel-specific volumes |
| Credit outstanding | Payment patterns |

**Unique:** Mechanics at tyre shops recommend brands. Fleet operators buy in bulk on contracts.

---

## 11. Batteries (Exide, Amara Raja)

**Who churns:** Dealers, mechanics, fleet operators

| Data Point | Description |
|------------|-------------|
| Dealer orders | Battery type, quantity, date |
| Old battery returns | Exchange scheme data |
| Warranty claims | Replacement under warranty |
| Mechanic program | Loyalty, referral tracking |
| Fleet contracts | Recurring orders from fleet companies |
| Seasonal patterns | Winter = higher battery failures |

**Unique:** Battery exchange programs create a reverse supply chain data point. Return rate predicts next purchase.

---

## 12. Lubricants (Castrol, Gulf Oil, Veedol)

**Who churns:** Distributors, mechanics, workshop owners

| Data Point | Description |
|------------|-------------|
| Distributor orders | SKU, volume, date |
| Mechanic/workshop purchases | Tracked via distributor |
| Bazaar (counter) sales | Retail purchases by vehicle owners |
| Mechanic loyalty program | Points, rewards |
| Oil change frequency | Vehicle service interval data (some) |
| Fleet contracts | Bulk supply agreements |

**Unique:** Mechanics are the primary recommenders. Their shift from one brand to another directly impacts distributor volumes.

---

## 13. Automobiles — OEM (Maruti, Tata, Mahindra, Hero, Bajaj)

**Who churns:** Dealers (switching brand or closing)

| Data Point | Description |
|------------|-------------|
| Vehicle dispatches | Model, variant, quantity, date |
| Dealer inventory | Aging stock |
| Booking pipeline | Customer bookings pending delivery |
| Test drive data | Lead conversion rates |
| After-sales service | Service revenue, parts sold |
| Customer satisfaction scores | NPS, CSI surveys |
| Financing penetration | Loans arranged by dealer |
| Dealer profitability | Margins, incentive payouts |

**Unique:** Service revenue is the profitability lever. Declining service visits = dealer disengagement.

---

## 14. Auto Components / Aftermarket (Bosch, Schaeffler, Minda)

**Who churns:** Distributors, garages, mechanics

| Data Point | Description |
|------------|-------------|
| Distributor orders | Part number, quantity, date |
| Garage/FME purchases | Via distributor billing |
| OES vs aftermarket split | Original vs replacement demand |
| Warranty claims | Defective parts returned |
| Mechanic training | Technical certification programs |
| Counter staff incentives | Points for recommending brand |

**Unique:** Counter sales staff at parts shops recommend brands. Their incentive redemption data matters.

---

## 15. Pharma (Sun Pharma, Cipla, Mankind, Abbott)

**Who churns:** Stockists, retailers (chemists), doctors (influencers)

| Data Point | Description |
|------------|-------------|
| Stockist orders | Drug/SKU, quantity, amount, date |
| Chemist secondary sales | Sell-out data (partial, via field force) |
| Doctor prescriptions | Tracked via MR (medical rep) call reports |
| MR visit frequency | Calls per doctor per month |
| Sample distribution | Free samples given to doctors |
| Prescription audits | IMS/IQVIA data on Rx share |
| Stockist credit | Outstanding, payment cycle |
| Expiry returns | Near-expiry stock returned |

**Unique:** Doctors are the influencers. MR call reports + prescription data = the churn signal. A doctor stopping prescriptions causes stockist volume drop.

---

## 16. Agri Inputs (UPL, Coromandel, PI Industries, Rallis, Dhanuka)

**Who churns:** Dealers, farmers (seasonal)

| Data Point | Description |
|------------|-------------|
| Dealer orders | Product, quantity, date |
| Farmer purchases (some) | Via dealer or field officer |
| Crop cycle data | Which crops, which season |
| Demo/trial plot results | Yield comparisons |
| Field officer visits | Farmer/dealer engagement frequency |
| Weather/rainfall | External factor affecting purchases |
| Credit/financing | Agri-credit schemes |
| Government scheme linkage | Subsidy-related purchases |

**Unique:** Purchases are seasonal (kharif/rabi). Year-on-year same-season comparison is the churn metric, not month-on-month.

---

## 17. Textiles & Apparel (Raymond, Page Industries, Aditya Birla Fashion)

**Who churns:** Retail franchisees, multi-brand outlet owners, distributors

| Data Point | Description |
|------------|-------------|
| Franchisee orders | SKU, quantity, amount, date |
| Sell-through rate | Retail sell-out vs sell-in ratio |
| Store footfall (owned stores) | POS data |
| Returns/exchanges | Unsold inventory returned |
| Category mix | Formal vs casual vs innerwear |
| Seasonal orders | Festival/wedding season spikes |
| Store performance | Sales per sq ft |

**Unique:** Sell-through rate is the key signal. High returns = retailer disengagement.

---

## 18. Footwear (Bata, Relaxo, Metro Brands, Campus)

**Who churns:** Franchisees, MBO (multi-brand outlet) owners, distributors

| Data Point | Description |
|------------|-------------|
| Dealer/franchisee orders | Style, size, quantity, date |
| Sell-through rate | Unsold pairs as % of dispatched |
| Returns | Size/style mismatches returned |
| Store display compliance | Brand shelf share |
| Season-specific orders | Monsoon, wedding, school |

**Unique:** Size and style accuracy matters. High return rates indicate poor demand sensing and precede churn.

---

## 19. Telecom Physical Distribution (Jio, Airtel, Vi)

**Who churns:** Retailers (recharge points), distributors

| Data Point | Description |
|------------|-------------|
| Retailer recharge transactions | Volume, value, date |
| SIM activations | New connections per retailer |
| Device sales | Handset sales through retailer |
| Commission earned | Retailer margins |
| Recharge denomination mix | Prepaid plan distribution |
| Retailer active days | Days with at least one transaction |
| Multi-brand stocking | Whether retailer sells rival SIMs |

**Unique:** Daily transaction granularity. A retailer going from 50 recharges/day to 10 is an immediate churn signal.

---

## Summary: Data Availability Matrix

| Vertical | Txn Data | Influencer Data | Loyalty Program | Service/Warranty | Seasonal | Credit |
|----------|----------|-----------------|-----------------|------------------|----------|--------|
| FMCG | Yes | No | No | No | Yes | Yes |
| Dairy | Yes | No | No | No | Yes | Yes |
| Paints | Yes | Yes (painters) | Yes | No | Yes | Yes |
| Adhesives | Yes | Yes (carpenters) | Yes | No | No | Yes |
| Tiles/Sanitaryware | Yes | Yes (architects) | No | No | No | Yes |
| Cement | Yes | Yes (masons) | Yes | No | Yes | Yes |
| Wires/Cables | Yes | Yes (electricians) | Yes | No | No | Yes |
| Steel Pipes | Yes | No | No | No | Yes | Yes |
| Consumer Durables | Yes | No | No | Yes | Yes | Yes |
| Tyres | Yes | Yes (mechanics) | Yes | Yes | No | Yes |
| Batteries | Yes | Yes (mechanics) | Yes | Yes | Yes | No |
| Lubricants | Yes | Yes (mechanics) | Yes | No | No | Yes |
| Automobiles OEM | Yes | No | No | Yes | Yes | Yes |
| Auto Aftermarket | Yes | Yes (mechanics) | Yes | Yes | No | Yes |
| Pharma | Yes | Yes (doctors) | No | No | No | Yes |
| Agri Inputs | Yes | Yes (farmers) | No | No | Yes | Yes |
| Textiles/Apparel | Yes | No | No | No | Yes | Yes |
| Footwear | Yes | No | No | No | Yes | Yes |
| Telecom Distribution | Yes | No | No | No | No | Yes |

---

## Key Insight for Product Scope

**Transaction-only verticals** (FMCG, dairy, steel pipes, textiles, footwear, telecom) — churn model uses purchase recency, frequency, monetary value, SKU mix, credit behavior.

**Transaction + influencer verticals** (paints, adhesives, cement, wires, tyres, batteries, lubricants, pharma, agri) — churn model can use influencer engagement as a leading indicator. Influencer disengagement predicts dealer volume decline before it shows in transactions.

The churn tool today handles transaction-only data. Adding influencer engagement data as an optional input would unlock the second (and higher-value) tier of verticals.
