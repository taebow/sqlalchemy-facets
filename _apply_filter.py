# def apply_filters(self, query: Query, selection: dict) -> Query:
#     return query.filter(
#         and_(
#             self.facets[name].filter(query, filter_config)
#             for name, filter_config in selection.items()
#             if name in self.facets.keys()
#         )
#     )

# In legacy facet class
# def filter(self, query: Query,
#            filter_config: Dict[str, Any]) -> BinaryExpression:
#     return get_column(query, self.column_name).in_(
#         [self.mapper.revert(v) for v in filter_config["values"]]
#     )