# schema_map.py
#
# Maps a pallet function's *resolved* type (see resolve_pallet_type() in
# parse_iflow.py - this is NOT always the same as the raw activityType,
# because SAP CPI reuses one activityType for several different pallet
# functions and disambiguates via a secondary property) to the exact
# table layout used in the TSD template.
#
# Each schema is:
#   {
#     "verified": True/False,   # True = property names checked against a
#                                # real production iFlow export. False =
#                                # best-effort from public documentation;
#                                # double check against your own export
#                                # before relying on it.
#     "title": "<Heading text used in the generated doc>",
#     "sections": [
#         ("<Sub-table header, e.g. 'General' / 'Processing'>", [
#             ("<Label shown in left column>", <field-spec>),
#             ...
#         ]),
#     ],
#   }
#
# <field-spec> is one of:
#   "SomePropertyKey"    -> plain value lookup, shown as-is
#   "__NAME__"           -> the element's own name attribute
#   {"bool": "PropKey"}
#       -> a single ☑/☐ with NO label text next to it (matches the
#          template's plain checkbox fields, e.g. "Delete On Completion ☐")
#   {"prop": "PropKey", "checkbox": ["OptA", "OptB"]}
#       -> renders every option with a box, checked when the raw stored
#          value textually matches that option (case-insensitive). Use
#          this only when the raw value IS the display text.
#   {"prop": "PropKey", "checkbox": {"rawvalue1": "Display Label 1", ...}}
#       -> same rendering, but maps the raw stored value (dict key,
#          case-insensitive) to the label shown (dict value). Use this
#          whenever the CPI-internal stored value differs from what the
#          UI/template displays (this is common - e.g. visibility is
#          stored as "local"/"global" but the template shows "Integration
#          Flow"/"Global").
#
# ONLY fields listed here are ever rendered for a given pallet function -
# there is no "show every extra property" fallback anymore. This keeps
# the document limited to what the template actually documents and out
# of internal/plumbing properties (component version numbers, SWCV ids,
# cmdVariantUri, etc.) that aren't visible anywhere in the CPI UI.

PALLET_SCHEMAS = {
    # ---- verified against a real production iFlow export ----
    "ContentModifier": {
        "verified": True,
        "title": "Content Modifier",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Message Body", [
                ("Type", {"prop": "bodyType", "checkbox": {"constant": "Constant", "expression": "Expression"}}),
                ("Body", "bodyContent"),
            ]),
            # Message Header / Exchange Property tables (headerTable /
            # propertyTable) are NOT listed here - they are nested CPI
            # "table inside a property" values, detected and rendered
            # automatically by generate_tsd.py as their own proper
            # Action/Name/Type/Datatype/Value/Default tables.
        ],
    },
    "GroovyScript": {
        "verified": True,
        "title": "Groovy Script",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Script File", "script"),
                ("Script Function", "scriptFunction"),
            ]),
        ],
    },
    "JavaScript": {
        "verified": False,  # same shape as GroovyScript by analogy; not
        # independently confirmed against a real JavaScript step.
        "title": "Java Script",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Script File", "script"),
                ("Script Function", "scriptFunction"),
            ]),
        ],
    },
    "ExternalCall": {
        "verified": True,
        "title": "Request-Reply (External Call)",
        "sections": [("General", [("Name", "__NAME__")])],
        # The External Call step itself carries almost no properties in
        # real exports - protocol/connection config lives entirely on the
        # adapter (message flow), which is rendered separately in the
        # Connectivity section.
    },
    "Send": {
        "verified": False,
        "title": "Send",
        "sections": [("General", [("Name", "__NAME__")])],
    },
    "ExclusiveGateway": {
        "verified": True,
        "title": "Router",
        "sections": [
            ("General", [
                ("Name", "__NAME__"),
                ("Error Handling", {"bool": "throwException"}),
            ]),
        ],
    },
    "ProcessCallElement": {
        "verified": True,
        "title": "Process Call",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [("Local Integration Process", "processId")]),
        ],
    },
    "LoopingProcessCallElement": {
        "verified": False,  # subActivityType value for the looping variant
        # is inferred (contains "loop"), not directly observed.
        "title": "Looping Process Call",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Local Integration Process", "processId"),
                ("Condition Expression", "conditionExpression"),
                ("Max. Number of Iterations", "maxIterations"),
            ]),
        ],
    },
    "DBstorage_Get": {
        "verified": True,
        "title": "Get (Data Store Operations)",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Data Store Name", "storageName"),
                ("Visibility", {"prop": "visibility", "checkbox": {"global": "Global", "local": "Integration Flow"}}),
                ("Entry ID", "dataStoreId"),
                ("Delete On Completion", {"bool": "delete"}),
                ("Throw Exception on Missing Entry", {"bool": "stopOnMissingEntry"}),
            ]),
        ],
    },
    "DBstorage_Select": {
        "verified": False,  # inferred to share DBstorage's Get field names;
        # not independently observed with operation=select.
        "title": "Select (Data Store Operations)",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Data Store Name", "storageName"),
                ("Visibility", {"prop": "visibility", "checkbox": {"global": "Global", "local": "Integration Flow"}}),
                ("Delete On Completion", {"bool": "delete"}),
            ]),
        ],
    },
    "DBstorage_Write": {
        "verified": False,
        "title": "Write (Data Store Operations)",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Data Store Name", "storageName"),
                ("Visibility", {"prop": "visibility", "checkbox": {"global": "Global", "local": "Integration Flow"}}),
                ("Entry ID", "dataStoreId"),
                ("Encrypt Stored Message", {"bool": "encryption"}),
                ("Overwrite Existing Message", {"bool": "overwrite"}),
            ]),
        ],
    },
    "DBstorage_Delete": {
        "verified": False,
        "title": "Delete (Data Store Operations)",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Data Store Name", "storageName"),
                ("Visibility", {"prop": "visibility", "checkbox": {"global": "Global", "local": "Integration Flow"}}),
                ("Entry ID", "dataStoreId"),
            ]),
        ],
    },
    "DBstorage_Persist": {
        "verified": False,
        "title": "Persist",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Encrypt Stored Message", {"bool": "encryption"}),
            ]),
        ],
    },
    "JsonToXmlConverter": {
        "verified": True,
        "title": "JSON to XML Convertor",
        "sections": [
            ("General", [
                ("Name", "__NAME__"),
                ("Use Namespace Mapping", {"bool": "useNamespaces"}),
            ]),
            ("Processing", [
                ("JSON Prefix Separator", "jsonNamespaceSeparator"),
                ("Add XML Root Element", {"bool": "addXMLRootElement"}),
            ]),
        ],
    },
    "XmlToJsonConverter": {
        "verified": False,  # not independently observed; assumed to mirror
        # JsonToXmlConverter's naming convention.
        "title": "XML to JSON Convertor",
        "sections": [
            ("General", [
                ("Name", "__NAME__"),
                ("Use Namespace Mapping", {"bool": "useNamespaces"}),
            ]),
            ("Processing", [
                ("JSON Prefix Separator", "jsonNamespaceSeparator"),
                ("Suppress Root Element", {"bool": "suppressJsonRootElement"}),
            ]),
        ],
    },
    "GeneralSplitter": {
        "verified": True,
        "title": "General Splitter",
        "sections": [
            ("General", [
                ("Name", "__NAME__"),
                ("Expression Type", {"prop": "exprType", "checkbox": {"xpath": "XPATH", "linebreak": "Line Break"}}),
                ("Xpath Expression", "splitExprValue"),
                ("Grouping", "grouping"),
                ("Time Out (in S)", "timeOut"),
                ("Streaming", {"bool": "Streaming"}),
                ("Parallel Processing", {"bool": "ParallelProcessing"}),
                ("Stop on Exception", {"bool": "StopOnExecution"}),
            ]),
        ],
    },
    "IteratingSplitter": {
        "verified": True,
        "title": "Iterating Splitter",
        "sections": [
            ("General", [
                ("Name", "__NAME__"),
                ("Expression Type", {"prop": "exprType", "checkbox": {"xpath": "XPATH", "linebreak": "Line Break", "token": "Token"}}),
                ("Xpath Expression", "splitExprValue"),
                ("Token", "tokenValue"),
                ("Grouping", "grouping"),
                ("Time Out (in S)", "timeOut"),
                ("Streaming", {"bool": "Streaming"}),
                ("Parallel Processing", {"bool": "ParallelProcessing"}),
                ("Stop on Exception", {"bool": "StopOnExecution"}),
            ]),
        ],
    },
    "XSLTMapping": {
        "verified": True,
        "title": "XSLT Mapping",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Source", "mappingSource"),
                ("Resource", "mappinguri"),
                ("Output Format", "mappingoutputformat"),
            ]),
        ],
    },
    "MessageMapping": {
        "verified": False,  # not observed in the reference export (it only
        # contained an XSLT mapping); field names inferred by analogy with
        # XSLTMapping's mappingSource/mappinguri convention.
        "title": "Message Mapping",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [("Resource", "mappinguri")]),
        ],
    },
    # ---- best-effort, not yet verified against a real export ----
    "ContentEnricher": {
        "verified": False,
        "title": "Content Enricher",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Aggregation Algorithm", {"prop": "aggregationAlgorithm", "checkbox": ["Combine", "Enrich"]}),
                ("Original Message", "sourceMessageBody"),
                ("Path to Node", "xpathSourceMessage"),
                ("Key Element", "xpathSourceMessageForKey"),
                ("Lookup Message", "lookupMessageBody"),
                ("Path to Node", "xpathLookupMessage"),
                ("Key Element", "xpathLookupMessageForKey"),
            ]),
        ],
    },
    "XmlValidator": {
        "verified": False,
        "title": "XML Validator",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Validation", [
                ("XML Schema", "schemaLocation"),
                ("Prevent Exception on Failure", {"bool": "continueOnException"}),
            ]),
        ],
    },
    "Filter": {
        "verified": False,
        "title": "Filter",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Xpath Expression", "xpathExpressionFilter"),
                ("Value Type", {"prop": "valueType", "checkbox": ["Boolean", "Integer", "Node", "Nodelist", "String"]}),
            ]),
        ],
    },
    "MessageDigest": {
        "verified": False,
        "title": "Message Digest",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Processing", [
                ("Filter (Xpath)", "digestXpath"),
                ("Digest Algorithm", "digestAlgorithm"),
                ("Target Header", "targetHeader"),
            ]),
        ],
    },
    "Aggregator": {
        "verified": False,
        "title": "Aggregator",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Correlation", [("Correlation Expression (Xpath)", "correlExpression")]),
            ("Aggregation Strategy", [
                ("Last Message Condition (Xpath)", "lastMessageCondition"),
                ("Message Sequence Expression (Xpath)", "predSuccExpression"),
                ("Completion Timeout (in min)", "completionTimeout"),
                ("Data Store Name", "datastore"),
            ]),
        ],
    },
    "Gather": {
        "verified": False,
        "title": "Gather",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Aggregation Strategy", [
                ("Incoming Format", "incomingFormat"),
                ("Combine from Source (Xpath)", "sourceXpath"),
                ("Combine at Target (Xpath)", "targetXpath"),
            ]),
        ],
    },
    "Join": {
        "verified": False,
        "title": "Join",
        "sections": [("General", [("Name", "__NAME__")])],
    },
    "Multicast": {
        "verified": False,
        "title": "Sequential Multicast",
        "sections": [("General", [("Name", "__NAME__")])],
    },
    "ParallelMulticast": {
        "verified": False,
        "title": "Parallel Multicast",
        "sections": [("General", [("Name", "__NAME__")])],
    },
}

ADAPTER_SCHEMAS = {
    # keyed by (ComponentType, direction) lowercased.
    "https|sender": {
        "verified": False,
        "title": "HTTPS Sender",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Connection", [
                ("Address", "Address"),
                ("User Role", "userRole"),
            ]),
        ],
    },
    "http|receiver": {
        "verified": True,  # field labels confirmed directly from a real
        # production export by the person using this tool.
        "title": "HTTP (HTTP - Receiver)",
        "sections": [
            ("General", [
                ("Name", "__NAME__"),
                ("Adapter / Component Type", "ComponentType"),
                ("Transport Protocol", "TransportProtocol"),
                ("Message Protocol", "MessageProtocol"),
            ]),
            ("Connection", [
                ("Address / Endpoint URL", ["Address", "httpAddressWithoutQuery"]),
                ("HTTP Method", "httpMethod"),
                ("Authentication Method", "authenticationMethod"),
                ("Credential Name", "credentialName"),
                ("Private Key Alias", "privateKeyAlias"),
                ("Location ID", "locationID"),
                ("Proxy Type", "proxyType"),
                ("Proxy Host", "proxyHost"),
                ("Proxy Port", "proxyPort"),
                ("Timeout (in ms)", "httpRequestTimeout"),
            ]),
            ("Processing", [
                ("Allowed Request Headers", "allowedRequestHeaders"),
                ("Allowed Response Headers", "allowedResponseHeaders"),
                ("Should Send Body", {"bool": "httpShouldSendBody"}),
                ("Throw Exception on Failure", {"bool": "throwExceptionOnFailure"}),
                ("Retry on Connection Failure", {"bool": "retryOnConnectionFailure"}),
                ("Retry Iteration", "retryIteration"),
                ("Retry Interval", "retryInterval"),
            ]),
        ],
    },
    "sftp|sender": {
        "verified": False,
        "title": "SFTP Sender",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Source", [
                ("Directory", "directory"),
                ("FileName", "fileName"),
                ("Address", "Address"),
            ]),
        ],
    },
    "sftp|receiver": {
        "verified": False,
        "title": "SFTP Receiver",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Target", [
                ("Directory", "directory"),
                ("File Name", "fileName"),
                ("Address", "Address"),
            ]),
        ],
    },
    "processdirect|sender": {
        "verified": False,
        "title": "Process Direct Sender",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Connection", [("Address", "Address")]),
        ],
    },
    "processdirect|receiver": {
        "verified": False,
        "title": "Process Direct Receiver",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Connection", [("Address", "Address")]),
        ],
    },
    "soap|sender": {
        "verified": False,
        "title": "SOAP Sender",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Connection", [("Address", "Address")]),
        ],
    },
    "soap|receiver": {
        "verified": False,
        "title": "SOAP Receiver",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Connection", [("Address", "Address")]),
        ],
    },
    "mail|receiver": {
        "verified": True,
        "title": "MAIL Receiver",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Connection", [
                ("Server", "server"),
                ("From", "from"),
                ("To", "to"),
                ("CC", "cc"),
                ("Subject", "subject"),
                ("Content Type", "content_type"),
            ]),
        ],
    },
    "idoc|receiver": {
        "verified": False,
        "title": "IDOC Receiver",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Connection", [("Address", "Address")]),
        ],
    },
    "odata|sender": {
        "verified": False,
        "title": "ODATA Sender",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Adapter-Specific", [("Operation", "operation")]),
        ],
    },
    "odata|receiver": {
        "verified": False,
        "title": "ODATA Receiver",
        "sections": [
            ("General", [("Name", "__NAME__")]),
            ("Adapter-Specific", [
                ("Address", "Address"),
                ("Operation", "operation"),
            ]),
        ],
    },
}
