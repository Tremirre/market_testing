from sim.asset import AssetManager
from sim.offer import OfferFactory
from sim.company import Company


class Market:
    def __init__(self):
        self.sell_offers = []
        self.buy_offers = []
        self.price_tracker = PriceTracker()
        self.companies = set()

    def initialize_market(self, initial_market_size=20, initial_price=5.0):
        self.companies.add(company := Company())
        for _ in range(initial_market_size):
            new_asset = AssetManager().create_asset(company)
            company.assets_for_sale.append(new_asset.id)
            offer = OfferFactory().create_offer(company, new_asset.id.company_id, initial_price, sell=True)
            self.add_sell_offer(offer)
        self.price_tracker.set_latest_asset_price(company.id, initial_price)

    def add_sell_offer(self, sell_offer):
        self.sell_offers.append(sell_offer)

    def add_buy_offer(self, buy_offer):
        self.buy_offers.append(buy_offer)

    def process_all_offers(self, transaction_limit=10):
        processed_transactions = []
        for i, sell_offer in enumerate(self.sell_offers):
            for j, buy_offer in enumerate(self.buy_offers):
                if sell_offer.asset_type == buy_offer.asset_type and sell_offer.min_sell_price <= buy_offer.max_buy_price:
                    self.process_offer(buy_offer, sell_offer)
                    processed_transactions.append(i)
                    self.buy_offers.pop(j)
                    break
            if len(processed_transactions) >= transaction_limit:
                self.remove_processed_sales(processed_transactions)
                return
        self.remove_processed_sales(processed_transactions)

    def process_offer(self, buy_offer, sell_offer):
        buyer = buy_offer.sender
        seller = sell_offer.sender
        asset_for_sale = seller.get_free_asset(buy_offer.asset_type)
        AssetManager().change_asset_owner(asset_for_sale, buyer)
        common_price = (buy_offer.max_buy_price + sell_offer.min_sell_price) / 2
        self.price_tracker.set_latest_asset_price(asset_for_sale.company_id, common_price)
        buyer.process_buy_order(asset_for_sale, common_price)
        if not isinstance(seller, Company):
            seller.process_sell_order(asset_for_sale, common_price)

    def get_asset_types(self):
        return [company.id for company in self.companies]

    def clear_market(self):
        new_sell = []
        for offer in self.sell_offers:
            if isinstance(offer.sender, Company):
                new_sell.append(offer)
        self.sell_offers = new_sell
        self.buy_offers = []

    def remove_sell_offer(self, offer_id):
        for i, offer in enumerate(self.sell_offers):
            if offer.offer_id == offer_id:
                self.sell_offers.pop(i)
                return

    def remove_buy_offer(self, offer_id):
        for i, offer in enumerate(self.buy_offers):
            if offer.offer_id == offer_id:
                self.buy_offers.pop(i)
                return

    def remove_processed_sales(self, list_of_sales):
        for index in sorted(list_of_sales, reverse=True):
            self.sell_offers.pop(index)

    def display_sell_offers(self):
        for offer in self.sell_offers:
            print(f"{offer.sender.name} offers asset {offer.asset_type} to sell for at least {offer.min_sell_price}")

    def display_buy_offers(self):
        for offer in self.buy_offers:
            print(f"{offer.sender.name} offers to buy asset {offer.asset_type} for at most {offer.max_buy_price}")


class PriceTracker:
    def __init__(self):
        self.asset_price = dict()

    def set_latest_asset_price(self, asset_id, price):
        self.asset_price[asset_id] = price

    def get_latest_asset_price(self, asset_id):
        return self.asset_price[asset_id]