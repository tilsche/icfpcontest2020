#pragma once

#include "simple_expr.hpp"

namespace zebra
{
struct FlatList;

using PFlatList = std::shared_ptr<FlatList>;
using FlatNode = std::variant<PFlatList, UnderlyingInteger>;

struct FlatList
{
    FlatList(bool is_terminated=false) : is_terminated(is_terminated) {

    }

    std::vector<FlatNode> data;
    bool is_terminated;
};

FlatNode flat_data(const SimpleNode& sn)
{
    if (std::holds_alternative<UnderlyingInteger>(sn)) {
        return {sn};
    }
    PFlatList pfl = std::make_shared<FlatList>();
    auto snp = &sn;
    while (std::holds_alternative<PSimpleCons>(*snp)) {
        pfl->data.emplace_back(flat_data(std::get<PSimpleCons>(*snp)->head));
        snp = std::get<PSimpleCons>(*snp)->tail;
    }
    if (std::holds_alternative<SimpleNil>(*snp))
    {
        pfl->is_terminated=true;
    } else {
        pfl->data.emplace_back(std::get<UnderlyingInteger>(*snp));
    }
    return {pfl};
}

FlatNode flat_data(const PExpr& expr)
{
    return flat_data(simple_data(expr));
}

inline std::ostream& operator<<(std::ostream& os, const FlatNode& fn)
{
    if (std::holds_alternative<UnderlyingInteger>(fn))
    {
        os << std::get<UnderlyingInteger>(fn);
    }
    else
    {
        const auto& list = *std::get<PFlatList>(fn);
        if (list.is_terminated) {
            os << "(";
        } else {
            os << "<";
        }
        first = true;
        for (const auto& e : list.data) {
            if (first) {
                first = false;
            } else {
                os << ", ";
            }
            os << e;
        }
    }
    return os;
}

} // namespace zebra