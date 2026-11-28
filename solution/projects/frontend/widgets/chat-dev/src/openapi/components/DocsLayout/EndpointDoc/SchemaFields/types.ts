/**
 * Tree-view schema model.
 *
 *  A ``FieldNode`` represents one row in the schema tree: either a
 *  primitive leaf (``string``, ``integer``, ``number``, ``boolean``) or
 *  a container (``object`` / ``array``) with children. Keeping children
 *  materialised (not lazy) makes the collapse state trivial — we know
 *  in advance whether a node is expandable.
 */

export type FieldKind = 'object' | 'array' | 'primitive';

export interface FieldNode {
    /** Leaf name. For arrays the node synthesises a pseudo-field named
     *  ``[]`` so the tree shows the ``items`` shape without the parent
     *  having to special-case array children. */
    name: string;
    /** Short type label — rendered alongside the name in the row. */
    type: string;
    kind: FieldKind;
    required: boolean;
    description?: string;
    /** Enum values when the field is an enum. Rendered as hint chips
     *  below the row when present and the caller opts in. */
    enumValues?: string[];
    /** Nested children — non-empty only for ``object`` / ``array`` kinds. */
    children?: FieldNode[];
}
