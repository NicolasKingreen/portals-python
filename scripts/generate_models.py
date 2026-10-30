from __future__ import annotations

import json
import keyword
import re
from pathlib import Path
from typing import Any

CLASS_NAMES = {
    "collection.FetchAllCollectionsWithPreviewOut": "CollectionsPreviewResponse",
    "collection.FetchAllUniqueAttributeFloorsOut": "AttributeFloorsResponse",
    "collection.FetchBackgroundFloorPricesOut": "FloorPricesResponse",
    "collection.FetchCollectionMetricsOut": "CollectionMetricsResponse",
    "collection.FetchModelsBackgroundsFloorPricesOut": "ModelBackgroundFloorsResponse",
    "collectionoffer.FetchCollectionsOut": "OfferCollectionsResponse",
    "collectionoffer.UpdateBatchFailedItem": "OfferUpdateFailure",
    "collectionoffer.UpdateBatchOut": "BulkUpdateOffersResponse",
    "dtocollectionfiltersrepo.AttributeFloorInfo": "AttributeFloorInfo",
    "dtocollectionfiltersrepo.FetchCollectionAttrFloorPricesOut": "CollectionAttributeFloorsMap",
    "dtocollectionoffers.CollectionInfo": "OfferCollection",
    "dtocollectionoffers.CollectionOfferItem": "CollectionOffer",
    "dtocollectionoffers.FetchTopOut": "CollectionOffersResponse",
    "dtonft.BulkListingResult": "BulkListingResult",
    "dtonft.FailedNft": "FailedNFT",
    "dwithdrawalsrepo.FetchStatusByIdOut": "TONWithdrawalStatusInfo",
    "exerr.HttpError": "ErrorResponse",
    "httpcollectionoffer.CreateOfferAttribute": "OfferAttribute",
    "httpcollectionoffer.CreateOfferResponse": "CollectionOffer",
    "httpmodel.Nft": "NFT",
    "httptrustedapps.AcceptOfferRequest": "AcceptOfferRequest",
    "httptrustedapps.BulkUpdateOfferItem": "BulkUpdateOfferItem",
    "httptrustedapps.BulkUpdateOffersRequest": "BulkUpdateOffersRequest",
    "httptrustedapps.CancelOfferRequest": "CancelOfferRequest",
    "httptrustedapps.CreateOfferRequest": "CreateOfferRequest",
    "httptrustedapps.arenaBet": "ArenaBet",
    "httptrustedapps.arenaBetRequest": "ArenaBetRequest",
    "httptrustedapps.arenaBetResponse": "ArenaBetResponse",
    "httptrustedapps.arenaGame": "ArenaGame",
    "httptrustedapps.arenaInventoryAttr": "ArenaInventoryAttribute",
    "httptrustedapps.arenaInventoryItem": "ArenaInventoryItem",
    "httptrustedapps.arenaInventoryResponse": "ArenaInventoryResponse",
    "httptrustedapps.arenaRoom": "ArenaRoom",
    "httptrustedapps.arenaStateResponse": "ArenaStateResponse",
    "httptrustedapps.fetchOwnedOut": "OwnedNFTsResponse",
    "httptrustedapps.generalOut": "MarketConfig",
    "httptrustedapps.searchNftsOut": "SearchNFTsResponse",
    "model.AnonymizedUserAction": "MarketAction",
    "model.AttributeFloorPrices": "AttributeFloorPrices",
    "model.Collection": "Collection",
    "model.CollectionAsset": "CollectionAsset",
    "model.CollectionMetrics": "CollectionMetrics",
    "model.CollectionOfferScope": "CollectionOfferScope",
    "model.CollectionWithPreview": "CollectionPreview",
    "model.DepositBonusClaimStatus": "DepositBonusClaimStatus",
    "model.DetailedUserAction": "UserAction",
    "model.Nft": "UserNFT",
    "model.NftAttribute": "NFTAttribute",
    "model.NftAttributeType": "NFTAttributeType",
    "model.NftDepositBonus": "NFTDepositBonus",
    "model.NftImportSource": "NFTImportSource",
    "model.NftStatus": "NFTStatus",
    "model.TonWithdrawalStatus": "TONWithdrawalStatus",
    "model.User": "User",
    "model.UserActionCollectionOffer": "ActionCollection",
    "model.UserActionNft": "ActionNFT",
    "model.UserActionOffer": "ActionOffer",
    "model.UserActionType": "UserActionType",
    "nft.AttributeFloorsMap": "AttributeFloors",
    "nft.BulkDelistIn": "BulkDelistRequest",
    "nft.BulkListForSaleIn": "BulkListRequest",
    "nft.BuyDetail": "BuyDetail",
    "nft.BuyPartialIn": "BuyRequest",
    "nft.BuyPartialOut": "BuyResponse",
    "nft.FetchUserStatsOut": "NFTStats",
    "nft.InvalidNftDetail": "InvalidNFT",
    "nft.InvalidNftReason": "InvalidNFTReason",
    "nft.ListForSaleIn": "ListNFTRequest",
    "nft.NftPriceDetail": "NFTPriceDetail",
    "nft.PurchaseResult": "PurchaseResult",
    "nft.TransferFailedItem": "TransferFailure",
    "nft.TransferGiftsIn": "TransferGiftsRequest",
    "nft.TransferGiftsOut": "TransferGiftsResponse",
    "nft.TransferRecipientInfo": "TransferRecipient",
    "nft.UpdatedNftDetail": "UpdatedNFT",
    "nft.WithdrawGiftsIn": "WithdrawGiftsRequest",
    "nft.WithdrawGiftsOut": "WithdrawGiftsResponse",
    "nft.WithdrawalStatus": "WithdrawalStatus",
    "nft.WithdrawalStatusesOut": "WithdrawalStatusesResponse",
    "user.CheckExistenceOut": "UserExistence",
    "usersactions.FetchAllUserActionsOut": "MarketActionsResponse",
    "usersactions.FetchUserActionsOut": "UserActionsResponse",
    "userwallet.GenerateDepositIdOut": "Deposit",
    "userwallet.InfoOut": "Wallet",
    "userwallet.WithdrawIn": "WithdrawTONRequest",
    "userwallet.WithdrawOut": "TONWithdrawal",
    "userwallet.WithdrawStatusOut": "TONWithdrawalStatuses",
}


HTTP_METHODS = ("get", "post", "put", "patch", "delete")
UNREFERENCED_RESPONSE_SCHEMAS = {"model.User"}


def python_name(value: str) -> str:
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value).lower()
    return f"{value}_" if keyword.iskeyword(value) else value


def literal(values: list[Any]) -> str:
    return f"Literal[{', '.join(repr(value) for value in values)}]"


def collect_refs(node: Any, out: set[str]) -> None:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            out.add(ref.rsplit("/", 1)[-1])
        for value in node.values():
            collect_refs(value, out)
    elif isinstance(node, list):
        for value in node:
            collect_refs(value, out)


def schema_closure(schemas: dict[str, Any], roots: set[str]) -> set[str]:
    seen: set[str] = set()
    stack = list(roots)
    while stack:
        name = stack.pop()
        if name in seen or name not in schemas:
            continue
        seen.add(name)
        refs: set[str] = set()
        collect_refs(schemas[name], refs)
        stack.extend(refs - seen)
    return seen


def classify_schemas(spec: dict[str, Any]) -> tuple[set[str], set[str]]:
    schemas = spec["components"]["schemas"]
    request_roots: set[str] = set()
    response_roots: set[str] = set()
    for item in spec["paths"].values():
        for method, operation in item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            collect_refs(operation.get("requestBody", {}), request_roots)
            collect_refs(operation.get("responses", {}), response_roots)

    request_schemas = schema_closure(schemas, request_roots)
    response_schemas = schema_closure(schemas, response_roots) | (
        UNREFERENCED_RESPONSE_SCHEMAS & set(schemas)
    )

    shared = request_schemas & response_schemas
    if shared:
        raise RuntimeError(f"Schemas reachable from both requests and responses: {sorted(shared)}")

    unclassified = set(schemas) - request_schemas - response_schemas
    if unclassified:
        raise RuntimeError(
            f"Unclassified schemas (not reachable from paths): {sorted(unclassified)}"
        )

    class_roles: dict[str, str] = {}
    for name in schemas:
        class_name = CLASS_NAMES[name]
        role = "request" if name in request_schemas else "response"
        previous = class_roles.setdefault(class_name, role)
        if previous != role:
            raise RuntimeError(f"Class {class_name} is mapped to both request and response schemas")

    return request_schemas, response_schemas


def generate_contract(spec: dict[str, Any]) -> str:
    version = spec.get("info", {}).get("version")
    if not isinstance(version, str) or not version.strip():
        raise RuntimeError("Missing or empty info.version in OpenAPI contract")
    return (
        "# Generated by scripts/generate_models.py from specs/partners.en.json.\n"
        f'__api_version__ = "{version}"\n'
    )


class Generator:
    def __init__(
        self,
        schemas: dict[str, Any],
        *,
        request_schemas: set[str],
    ) -> None:
        self.schemas = schemas
        self.request_schemas = request_schemas
        self.output: list[str] = []
        self.rendered: set[str] = set()

    def ref_name(self, ref: str) -> str:
        return CLASS_NAMES[ref.rsplit("/", 1)[-1]]

    def field_type(self, schema: dict[str, Any]) -> str:
        if "$ref" in schema:
            return self.ref_name(schema["$ref"])
        if "allOf" in schema:
            return self.field_type(schema["allOf"][0])
        if "enum" in schema:
            return literal(schema["enum"])
        description = schema.get("description", "").lower()
        kind = schema.get("type")
        if kind == "string":
            if "decimal string" in description:
                return "Amount"
            if any(marker in description for marker in ("date-time", "rfc 3339", "iso 8601")):
                return "datetime"
            return "str"
        if kind == "integer":
            return "int"
        if kind == "number":
            return "float"
        if kind == "boolean":
            return "bool"
        if kind == "array":
            return f"list[{self.field_type(schema.get('items', {}))}]"
        if kind == "object" or "additionalProperties" in schema:
            additional = schema.get("additionalProperties")
            if additional is None:
                return "dict[str, Any]"
            if additional == {}:
                value_type = "Any"
            elif "decimal string" in description and additional.get("type") == "string":
                value_type = "Amount"
            else:
                value_type = self.field_type(additional)
            return f"dict[str, {value_type}]"
        return "Any"

    def render_enum(self, class_name: str, schema: dict[str, Any]) -> None:
        lines = [f"class {class_name}(StrEnum):"]
        used: set[str] = set()
        for value in schema["enum"]:
            member = re.sub(r"[^A-Za-z0-9]+", "_", str(value)).strip("_").upper()
            if member[0].isdigit():
                member = f"VALUE_{member}"
            original = member
            suffix = 2
            while member in used:
                member = f"{original}_{suffix}"
                suffix += 1
            used.add(member)
            lines.append(f"    {member} = {value!r}")
        self.output.append("\n".join(lines))

    def render_object(
        self,
        class_name: str,
        schema: dict[str, Any],
        *,
        base_class: str = "PortalsResponse",
    ) -> None:
        required = set(schema.get("required", []))
        lines = [f"class {class_name}({base_class}):"]
        properties = schema.get("properties", {})
        if not properties:
            lines.append("    pass")
        for wire_name, field_schema in properties.items():
            name = python_name(wire_name)
            annotation = self.field_type(field_schema)
            if wire_name not in required or field_schema.get("nullable"):
                annotation = f"{annotation} | None"
            arguments: list[str] = []
            if wire_name not in required:
                arguments.append("default=None")
            if name != wire_name:
                arguments.append(f"alias={wire_name!r}")
            constraints = self.constraints(field_schema)
            arguments.extend(constraints)
            if arguments:
                assignment = f"Field({', '.join(arguments)})"
            else:
                assignment = "Field()"
            lines.append(f"    {name}: {annotation} = {assignment}")
        self.output.append("\n".join(lines))

    @staticmethod
    def constraints(schema: dict[str, Any]) -> list[str]:
        arguments: list[str] = []
        if "minimum" in schema:
            arguments.append(f"ge={schema['minimum']}")
        if "maximum" in schema:
            arguments.append(f"le={schema['maximum']}")
        if "minItems" in schema:
            arguments.append(f"min_length={schema['minItems']}")
        if "maxItems" in schema:
            arguments.append(f"max_length={schema['maxItems']}")
        return arguments

    def generate(self) -> str:
        for name, schema in self.schemas.items():
            class_name = CLASS_NAMES[name]
            if class_name in self.rendered:
                continue
            self.rendered.add(class_name)
            if "enum" in schema:
                self.render_enum(class_name, schema)
            elif schema.get("type") == "object" and not schema.get("properties"):
                annotation = self.field_type(schema)
                if name == "dtocollectionfiltersrepo.FetchCollectionAttrFloorPricesOut":
                    nested = schema["additionalProperties"]
                    self.render_object("CollectionAttributeFloors", nested)
                    annotation = "dict[str, CollectionAttributeFloors]"
                elif name == "model.AttributeFloorPrices":
                    annotation = "dict[str, Amount]"
                self.output.append(f"{class_name} = {annotation}")
            else:
                base_class = "PortalsRequest" if name in self.request_schemas else "PortalsResponse"
                self.render_object(class_name, schema, base_class=base_class)

        header = """# Generated by scripts/generate_models.py from specs/partners.en.json.
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import Field

from ._models import Amount, PortalsRequest, PortalsResponse

"""
        exports = sorted(set(CLASS_NAMES.values()) | {"CollectionAttributeFloors"})
        all_definition = (
            "\n\n__all__ = [\n" + "".join(f"    {name!r},\n" for name in exports) + "]\n"
        )
        return header + "\n" + "\n\n\n".join(self.output) + all_definition


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    with (root / "specs" / "partners.en.json").open() as file:
        spec = json.load(file)
    schemas = spec["components"]["schemas"]
    missing = set(schemas) - set(CLASS_NAMES)
    extra = set(CLASS_NAMES) - set(schemas)
    if missing or extra:
        raise RuntimeError(f"Schema mapping mismatch: missing={missing}, extra={extra}")
    request_schemas, _ = classify_schemas(spec)
    output = Generator(schemas, request_schemas=request_schemas).generate()
    (root / "src" / "portals" / "models.py").write_text(output)
    (root / "src" / "portals" / "_contract.py").write_text(generate_contract(spec))


if __name__ == "__main__":
    main()
