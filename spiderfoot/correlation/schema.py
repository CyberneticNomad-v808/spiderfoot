# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:         Modular SpiderFoot Correlation Engine
# Purpose:      Common functions for enriching events with contextual information.
#
# Author:      Agostino Panico @poppopjmp
#
# Created:     30/06/2025
# Copyright:   (c) Agostino Panico 2025
# Licence:     MIT
# -------------------------------------------------------------------------------
# JSON Schema for correlation rules
RULE_SCHEMA = {
    "type": "object",
    "properties": {
        "meta": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "risk": {"type": "string"},
                "author": {"type": "string"},
                "url": {"type": "string"},
                "version": {"type": "string"},
                "scope": {"type": "string", "enum": ["scan", "workspace", "global"]}
            },
            "required": ["name", "description", "risk"]
        },
        "collections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "condition": {"type": "object"}
                },
                "required": ["id", "name", "condition"]
            }
        },
        "aggregation": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "collections": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "key": {"type": "string"}
                }
            }
        },
        "analysis": {
            "type": "object",
            "properties": {
                "method": {"type": "string"},
                "conditions": {"type": "array"}
            }
        },
        "headline": {"type": "string"},
        "enabled": {"type": "boolean"},
        "id": {"type": "string"},
        "version": {"type": "string"},
        "extra": {"type": "object"}
    },
    "required": ["meta", "collections", "headline"]
}
