// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

package pkggraph

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
	"gonum.org/v1/gonum/graph"
	"microsoft.com/pkggen/internal/logger"
	"microsoft.com/pkggen/internal/pkgjson"
)

// Note about test data:
// The nodes listed will NOT be found in an actual graph, they are just representative copies which can be used for equality
// testing and as a source to build real nodes from.

//
// Full Test Graph:
//	A(v1):
//	-> D(v<1)
//	-> B(v2):
//		-> C(v3-3):
//			-> D(v=3)
//		-> D(v<=2)
//	C(v3-4):
//		-> D(V>=4)
//		-> D(V>5)
//		-> D(V>6,<7)
var (
	pkgA      = pkgjson.PackageVer{Name: "A", Version: "1"}
	pkgARun   = buildRunNodeHelper(&pkgA)
	pkgABuild = buildBuildNodeHelper(&pkgA)

	pkgB      = pkgjson.PackageVer{Name: "B", Version: "2"}
	pkgBRun   = buildRunNodeHelper(&pkgB)
	pkgBBuild = buildBuildNodeHelper(&pkgB)

	pkgC      = pkgjson.PackageVer{Name: "C", Version: "3-3"}
	pkgCRun   = buildRunNodeHelper(&pkgC)
	pkgCBuild = buildBuildNodeHelper(&pkgC)

	pkgC2      = pkgjson.PackageVer{Name: "C", Version: "3-4"}
	pkgC2Run   = buildRunNodeHelper(&pkgC2)
	pkgC2Build = buildBuildNodeHelper(&pkgC2)

	pkgD1           = pkgjson.PackageVer{Name: "D", Version: "1", Condition: "<"}
	pkgD1Unresolved = buildUnresolvedNodeHelper(&pkgD1)
	pkgD2           = pkgjson.PackageVer{Name: "D", SVersion: "2", SCondition: "<="}
	pkgD2Unresolved = buildUnresolvedNodeHelper(&pkgD2)
	pkgD3           = pkgjson.PackageVer{Name: "D", Version: "3", Condition: "="}
	pkgD3Unresolved = buildUnresolvedNodeHelper(&pkgD3)
	pkgD4           = pkgjson.PackageVer{Name: "D", Version: "4", Condition: ">="}
	pkgD4Unresolved = buildUnresolvedNodeHelper(&pkgD4)
	pkgD5           = pkgjson.PackageVer{Name: "D", Version: "5", Condition: ">"}
	pkgD5Unresolved = buildUnresolvedNodeHelper(&pkgD5)
	pkgD6           = pkgjson.PackageVer{Name: "D", Version: "6", Condition: ">", SVersion: "7", SCondition: "<"}
	pkgD6Unresolved = buildUnresolvedNodeHelper(&pkgD6)

	pkgVersions     = []*pkgjson.PackageVer{&pkgA, &pkgB, &pkgC, &pkgC2, &pkgD1, &pkgD2, &pkgD3, &pkgD4, &pkgD5, &pkgD6}
	runNodes        = []*PkgNode{pkgARun, pkgBRun, pkgCRun, pkgC2Run}
	buildNodes      = []*PkgNode{pkgABuild, pkgBBuild, pkgCBuild, pkgC2Build}
	unresolvedNodes = []*PkgNode{pkgD1Unresolved, pkgD2Unresolved, pkgD3Unresolved, pkgD4Unresolved, pkgD5Unresolved, pkgD6Unresolved}

	allNodes = []*PkgNode{pkgARun, pkgBRun, pkgCRun, pkgC2Run,
		pkgABuild, pkgBBuild, pkgCBuild, pkgC2Build,
		pkgD1Unresolved, pkgD2Unresolved, pkgD3Unresolved, pkgD4Unresolved, pkgD5Unresolved, pkgD6Unresolved}

	edges = [][]*PkgNode{
		{pkgARun, pkgABuild},
		{pkgABuild, pkgBRun},
		{pkgARun, pkgD1Unresolved},

		{pkgBRun, pkgBBuild},
		{pkgBBuild, pkgCRun},
		{pkgBRun, pkgD2Unresolved},

		{pkgCRun, pkgCBuild},
		{pkgCRun, pkgD3Unresolved},

		{pkgC2Run, pkgC2Build},
		{pkgC2Run, pkgD4Unresolved},
		{pkgC2Run, pkgD5Unresolved},
		{pkgC2Run, pkgD6Unresolved},
	}
)

func TestMain(m *testing.M) {
	logger.InitStderrLog()
	os.Exit(m.Run())
}

// buildRunNode creates a new 'Run' PkgNode based on a PackageVer struct
func buildRunNodeHelper(pkg *pkgjson.PackageVer) (node *PkgNode) {
	var pkgCopy pkgjson.PackageVer
	pkgCopy = *pkg
	node = &PkgNode{
		VersionedPkg: &pkgCopy,
		State:        StateMeta,
		Type:         TypeRun,
		SrpmPath:     pkgCopy.Name + ".src.rpm",
		RpmPath:      pkgCopy.Name + ".rpm",
		SpecPath:     pkgCopy.Name + ".spec",
		SourceDir:    pkgCopy.Name + "/src/",
		Architecture: "test_arch",
		SourceRepo:   "test_repo",
	}
	node.This = node
	return
}

// buildBuildNode creates a new 'Build' PkgNode based on a PackageVer struct
func buildBuildNodeHelper(pkg *pkgjson.PackageVer) (node *PkgNode) {
	var pkgCopy pkgjson.PackageVer
	pkgCopy = *pkg
	node = &PkgNode{
		VersionedPkg: &pkgCopy,
		State:        StateBuild,
		Type:         TypeBuild,
		SrpmPath:     pkgCopy.Name + ".src.rpm",
		RpmPath:      pkgCopy.Name + ".rpm",
		SpecPath:     pkgCopy.Name + ".spec",
		SourceDir:    pkgCopy.Name + "/src/",
		Architecture: "test_arch",
		SourceRepo:   "test_repo",
	}
	node.This = node
	return
}

// buildBuildNode creates a new 'Unresolved' PkgNode based on a PackageVer struct
func buildUnresolvedNodeHelper(pkg *pkgjson.PackageVer) (node *PkgNode) {
	var pkgCopy pkgjson.PackageVer
	pkgCopy = *pkg
	node = &PkgNode{
		VersionedPkg: &pkgCopy,
		State:        StateUnresolved,
		Type:         TypeRemote,
		SrpmPath:     "url://" + pkgCopy.Name + ".src.rpm",
		RpmPath:      "url://" + pkgCopy.Name + ".rpm",
		SpecPath:     "url://" + pkgCopy.Name + ".spec",
		SourceDir:    "url://" + pkgCopy.Name + "/src/",
		Architecture: "test_arch",
		SourceRepo:   "test_repo",
	}
	node.This = node
	return
}

// addNodeToGraphHelper adds a copy of a node to the graph
func addNodeToGraphHelper(g *PkgGraph, node *PkgNode) (newNode *PkgNode, err error) {
	newNode, err = g.AddPkgNode(
		node.VersionedPkg,
		node.State,
		node.Type,
		node.SrpmPath,
		node.RpmPath,
		node.SpecPath,
		node.SourceDir,
		node.Architecture,
		node.SourceRepo,
	)
	return
}

// Adds copies of each node in a list to a graph
func addNodesHelper(g *PkgGraph, nodes []*PkgNode) (err error) {
	for _, n := range nodes {
		_, err = addNodeToGraphHelper(g, n)
		if err != nil {
			return
		}
	}
	return
}

// Add edges to the graph. Nodes must be found in the lookup table since this is
// meant to work based on copies of the nodes.
func addEdgeHelper(g *PkgGraph, pkg1 PkgNode, pkg2 PkgNode) (err error) {
	var (
		lu1, lu2 *LookupNode
		n1, n2   *PkgNode
	)

	lu1, err = g.FindExactPkgNodeFromPkg(pkg1.VersionedPkg)
	if lu1 == nil || err != nil {
		return fmt.Errorf("couldn't find %s (%v)", pkg1.String(), lu1)
	}
	lu2, err = g.FindExactPkgNodeFromPkg(pkg2.VersionedPkg)
	if lu2 == nil || err != nil {
		return fmt.Errorf("couldn't find %s (%v)", pkg2.String(), lu2)
	}

	if pkg1.Type == TypeBuild {
		n1 = lu1.BuildNode
	} else {
		n1 = lu1.RunNode
	}

	if pkg2.Type == TypeBuild {
		n2 = lu2.BuildNode
	} else {
		n2 = lu2.RunNode
	}

	edge := g.NewEdge(n1, n2)
	g.SetEdge(edge)

	return
}

// Builds the simple test graph described above.
func buildTestGraphHelper() (g *PkgGraph, err error) {
	g = NewPkgGraph()
	err = addNodesHelper(g, allNodes)
	for _, edgePair := range edges {
		err = addEdgeHelper(g, *edgePair[0], *edgePair[1])
	}
	return
}

func checkTestGraph(t *testing.T, g *PkgGraph) {
	// Make sure we got the same graph back!
	assert.Equal(t, len(allNodes), len(g.AllNodes()))
	assert.Equal(t, len(runNodes)+len(unresolvedNodes), len(g.AllRunNodes()))
	assert.Equal(t, len(buildNodes), len(g.AllBuildNodes()))

	// Check the correctness of the disconnected components rooted in pkgARun, and pkgC2Run
	a, err := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "A"})
	assert.NoError(t, err)
	component1 := []*PkgNode{
		pkgARun,
		pkgABuild,
		pkgBRun,
		pkgBBuild,
		pkgCRun,
		pkgCBuild,
		pkgD1Unresolved,
		pkgD2Unresolved,
		pkgD3Unresolved,
	}
	for _, mustHave := range component1 {
		found := false
		for _, n := range g.AllNodesFrom(a.RunNode) {
			found = found || mustHave.Equal(n)
		}
		assert.True(t, found)
	}
	assert.Equal(t, len(component1), len(g.AllNodesFrom(a.RunNode)))

	c2, err := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "C"})
	assert.NoError(t, err)
	component2 := []*PkgNode{
		pkgC2Run,
		pkgC2Build,
		pkgD4Unresolved,
		pkgD5Unresolved,
		pkgD6Unresolved,
	}
	for _, mustHave := range component2 {
		found := false
		for _, n := range g.AllNodesFrom(c2.RunNode) {
			found = found || mustHave.Equal(n)
		}
		assert.True(t, found)
	}
	assert.Equal(t, len(component2), len(g.AllNodesFrom(c2.RunNode)))
}

// Validate the test graph is well formed
func TestCreateTestGraph(t *testing.T) {
	g, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, g)
	assert.Equal(t, len(allNodes), len(g.AllNodes()))
	assert.Equal(t, len(runNodes)+len(unresolvedNodes), len(g.AllRunNodes()))
	assert.Equal(t, len(buildNodes), len(g.AllBuildNodes()))

	// Check the correctness of the disconnected components rooted in pkgARun, and pkgC2Run
	checkTestGraph(t, g)
}

// TestNodeStateString checks the NoteState -> string functionality
func TestNodeStateString(t *testing.T) {
	assert.Equal(t, "Meta", StateMeta.String())
	assert.Equal(t, "Build", StateBuild.String())
	assert.Equal(t, "BuildError", StateBuildError.String())
	assert.Equal(t, "UpToDate", StateUpToDate.String())
	assert.Equal(t, "Unresolved", StateUnresolved.String())
	assert.Equal(t, "Cached", StateCached.String())
	var s NodeState
	s = -1
	assert.Panics(t, func() { _ = s.String() })
	for s = StateUnknown + 1; s <= StateMAX; s++ {
		assert.NotPanics(t, func() { _ = s.String() })
	}
}

// TestNodeTypeString checks the NodeType -> string functionality
func TestNodeTypeString(t *testing.T) {
	assert.Equal(t, "Build", TypeBuild.String())
	assert.Equal(t, "Run", TypeRun.String())
	assert.Equal(t, "Goal", TypeGoal.String())
	assert.Equal(t, "Remote", TypeRemote.String())
	assert.Equal(t, "PureMeta", TypePureMeta.String())
	assert.Equal(t, "PreBuilt", TypePreBuilt.String())
	var tp NodeType
	tp = -1
	assert.Panics(t, func() { _ = tp.String() })
	for tp = TypeUnknown + 1; tp <= TypeMAX; tp++ {
		assert.NotPanics(t, func() { _ = tp.String() })
	}
}

// TestDOTColor checks that every combination of state and type give a color
func TestDOTColor(t *testing.T) {
	var (
		st NodeState
		tp NodeType
	)
	for st = StateUnknown + 1; st <= StateMAX; st++ {
		for tp = TypeUnknown + 1; tp <= TypeMAX; tp++ {
			n := PkgNode{State: st, Type: tp}
			assert.NotPanics(t, func() { n.DOTColor() })
			assert.True(t, len(n.DOTColor()) > 0)
		}
	}
	n := PkgNode{State: -1, Type: -1}
	assert.Panics(t, func() { n.DOTColor() })
}

// TestDOTID checks that nodes will generate the correct DOTID for serialization.
func TestDOTID(t *testing.T) {
	for _, n := range allNodes {
		assert.NotPanics(t, func() { n.DOTID() })
	}
	assert.Equal(t, "A-1-RUN<Meta> (ID=0,TYPE=Run,STATE=Meta)", pkgARun.DOTID())
	assert.Equal(t, "D--REMOTE<Unresolved> (ID=0,TYPE=Remote,STATE=Unresolved)", pkgD1Unresolved.DOTID())

	g := NewPkgGraph()
	goal, err := g.AddGoalNode("test", nil, false)
	assert.NoError(t, err)
	assert.Equal(t, "test (ID=0,TYPE=Goal,STATE=Meta)", goal.DOTID())

	meta := g.AddMetaNode([]*PkgNode{}, []*PkgNode{})
	assert.Equal(t, "Meta(1) (ID=1,TYPE=PureMeta,STATE=Meta)", meta.DOTID())

	junk := PkgNode{State: -1, Type: -1}
	assert.Panics(t, func() { junk.DOTID() })
}

// TestNodeString tests the built-in String() function for PkgNodes
func TestNodeString(t *testing.T) {
	assert.Equal(t, "A(1,):<ID:0 Type:Run State:Meta Rpm:A.rpm> from 'A.src.rpm' in 'test_repo'", pkgARun.String())
	assert.Equal(t, "D(<1,):<ID:0 Type:Remote State:Unresolved Rpm:url://D.rpm> from 'url://D.src.rpm' in 'test_repo'", pkgD1Unresolved.String())
	goalNode := PkgNode{GoalName: "goal", Type: TypeGoal, State: StateMeta}
	assert.Equal(t, "goal():<ID:0 Type:Goal State:Meta Rpm:> from '' in ''", goalNode.String())
	emptyNode := PkgNode{}
	assert.Panics(t, func() { _ = emptyNode.String() })
}

// TestNodeEquality checks equality with both identical pointers and copies of a PkgNode
func TestNodeEquality(t *testing.T) {
	assert.True(t, pkgARun.Equal(pkgARun))
	pkgAAlt := buildRunNodeHelper(&pkgA)
	assert.True(t, pkgAAlt.Equal(pkgARun))
}

// TestNodeInequality checks inequality for PkgNodes
func TestNodeInequality(t *testing.T) {
	assert.False(t, pkgARun.Equal(pkgABuild))
	assert.False(t, pkgARun.Equal(pkgBRun))
}

// Add a single Run node to the graph
func TestAddNode(t *testing.T) {
	g := NewPkgGraph()
	newNode, err := addNodeToGraphHelper(g, pkgARun)

	assert.Equal(t, nil, err)
	assert.NotEqual(t, newNode, nil)
	assert.True(t, newNode.Equal(pkgARun))
	assert.Equal(t, 1, len(g.AllNodes()))
}

// Add multiple run, then build, nodes to a graph
func TestAddMultipleNodes(t *testing.T) {
	g := NewPkgGraph()
	assert.NotNil(t, g)
	err := addNodesHelper(g, runNodes)
	assert.NoError(t, err)
	err = addNodesHelper(g, buildNodes)
	assert.NoError(t, err)

	assert.Equal(t, len(runNodes)+len(buildNodes), len(g.AllNodes()))
	assert.Equal(t, len(runNodes), len(g.AllRunNodes()))
	assert.Equal(t, len(buildNodes), len(g.AllBuildNodes()))
}

// Add an unresolved node to the graph
func TestAddUnresolvedNode(t *testing.T) {
	g := NewPkgGraph()
	n, err := addNodeToGraphHelper(g, pkgD1Unresolved)
	assert.NoError(t, err)
	assert.NotNil(t, n)
}

// Add a node with a missing primary version
func TestAddMissingVersion(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, runNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)
	err = addNodesHelper(g, buildNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	n, err := addNodeToGraphHelper(g, pkgD2Unresolved)
	assert.NoError(t, err)
	assert.NotNil(t, n)

}

// Add a run node with an invalid version (for a run node)
func TestAddBadVersionCond(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	for _, cond := range []string{"<", "<=", ">", "????"} {
		ver := &pkgjson.PackageVer{Name: "bad_ver", Version: "1", Condition: cond}
		_, err = addNodeToGraphHelper(g, buildRunNodeHelper(ver))
		assert.Error(t, err)
	}
}

// Make sure we can add valid conditional nodes, then find them again
func TestGoodVersionCond(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	for _, cond := range []string{">=", "=", ""} {
		ver := &pkgjson.PackageVer{Name: "good_ver" + cond, Version: "1", Condition: cond}
		n, err := addNodeToGraphHelper(g, buildRunNodeHelper(ver))
		assert.NoError(t, err)
		assert.NotNil(t, n)

		lookup, err := g.FindBestPkgNode(ver)
		assert.NoError(t, err)
		assert.NotNil(t, lookup)
		assert.True(t, n.Equal(lookup.RunNode))
	}
}

// Make sure we can't add a run node with multiple conditions
func TestDisallowMultiConditionals(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	ver := &pkgjson.PackageVer{Name: "bad_multi_ver", Version: "1", Condition: ">=", SCondition: "<", SVersion: "2"}
	_, err = addNodeToGraphHelper(g, buildRunNodeHelper(ver))
	assert.Error(t, err)
}

// Check basic lookup using the C package which as two versions.
func TestLookupNodeBasic(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	lNode, err := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "C"})

	assert.Equal(t, nil, err)
	assert.NotEqual(t, lNode, nil)
	assert.NotEqual(t, lNode.RunNode, nil)
	// Make sure we got the latest version
	assert.True(t, lNode.RunNode.Equal(pkgC2Run))
}

// Check we can get the exact node we want
func TestLookupNodeExact(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	for _, pkg := range pkgVersions {
		lNode, err := g.FindExactPkgNodeFromPkg(pkg)
		assert.NoError(t, err)
		assert.NotNil(t, lNode)
		assert.NotNil(t, lNode.RunNode)
		assert.True(t, lNode.RunNode.VersionedPkg.Name == pkg.Name)

		if lNode.RunNode.State != StateUnresolved {
			assert.NotNil(t, lNode.BuildNode)
			assert.True(t, lNode.BuildNode.VersionedPkg.Name == pkg.Name)
		}
	}
}

func TestLookupNoVersion(t *testing.T) {
	g := NewPkgGraph()
	n := buildUnresolvedNodeHelper(&pkgjson.PackageVer{Name: "test"})
	_, err := addNodeToGraphHelper(g, n)
	assert.NoError(t, err)
	lu, err := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "test"})
	assert.NoError(t, err)
	assert.NotNil(t, lu)
	assert.True(t, lu.RunNode.Equal(n))
}

// Check we can search with basic conditionals
func TestConditionalLookupBasic(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	// Highest version should be C2 (ver3-4)
	lu, err := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "C", Version: "3-3", Condition: ">"})
	assert.NoError(t, err)
	assert.NotNil(t, lu)
	assert.True(t, lu.RunNode.Equal(pkgC2Run))

	// Need lower than 3-4, we should get C with ver3-3
	lu, err = g.FindBestPkgNode(&pkgjson.PackageVer{Name: "C", Version: "3-4", Condition: "<"})
	assert.NoError(t, err)
	assert.NotNil(t, lu)
	assert.True(t, lu.RunNode.Equal(pkgCRun))

	// Best is D2, which is ver: <=2
	lu, err = g.FindBestPkgNode(&pkgjson.PackageVer{Name: "D", Version: "1"})
	assert.NoError(t, err)
	assert.NotNil(t, lu)
	assert.True(t, lu.RunNode.Equal(pkgD2Unresolved))

	lu, err = g.FindBestPkgNode(&pkgjson.PackageVer{Name: "D", Version: "2.1"})
	assert.NoError(t, err)
	assert.Nil(t, lu)
}

// Test searching for nodes using multiple conditions
func TestConditionalLookupMulti(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, unresolvedNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	// Should get D2 (<= 2)
	lu, err := g.FindBestPkgNode(&pkgjson.PackageVer{
		Name:       "D",
		Condition:  ">=",
		Version:    "1",
		SCondition: "<",
		SVersion:   "3"})
	assert.NoError(t, err)
	assert.True(t, lu.RunNode.Equal(pkgD2Unresolved))

	lu, err = g.FindBestPkgNode(&pkgjson.PackageVer{
		Name:       "D",
		Condition:  ">=",
		Version:    "2",
		SCondition: "<",
		SVersion:   "3"})
	assert.NoError(t, err)
	assert.True(t, lu.RunNode.Equal(pkgD2Unresolved))

	lu, err = g.FindBestPkgNode(&pkgjson.PackageVer{
		Name:       "D",
		Condition:  ">=",
		Version:    "2",
		SCondition: "<=",
		SVersion:   "3"})
	assert.NoError(t, err)
	assert.True(t, lu.RunNode.Equal(pkgD3Unresolved))

	lu, err = g.FindBestPkgNode(&pkgjson.PackageVer{
		Name:       "D",
		Condition:  "<",
		Version:    "3",
		SCondition: ">",
		SVersion:   "3"})
	assert.Error(t, err)
	assert.Nil(t, lu)
}

// Verify we can search for nodes when the first conditional is missing
func TestConditionalLookupMultiMissingFirst(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	// Should get D2 (<= 2)
	lu, err := g.FindBestPkgNode(&pkgjson.PackageVer{
		Name:       "A",
		SCondition: "=",
		SVersion:   "1"})
	assert.NoError(t, err)
	assert.True(t, lu.RunNode.Equal(pkgARun))

	lu, err = g.FindBestPkgNode(&pkgjson.PackageVer{
		Name:       "A",
		SCondition: "=",
		SVersion:   "2"})
	assert.NoError(t, err)
	assert.Nil(t, lu)
}

// Make sure we get the newest valid version when we search
func TestFindNewest(t *testing.T) {
	n1 := &pkgjson.PackageVer{Name: "n", Version: "1"}
	n1Run := buildRunNodeHelper(n1)
	n2 := &pkgjson.PackageVer{Name: "n", Version: "2"}
	n2Run := buildRunNodeHelper(n2)
	n3 := &pkgjson.PackageVer{Name: "n", Version: "3"}
	n3Run := buildRunNodeHelper(n3)

	g := NewPkgGraph()
	assert.NotNil(t, g)

	_, err := addNodeToGraphHelper(g, n2Run)
	assert.NoError(t, err)
	lu, err := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "n"})
	assert.NoError(t, err)
	assert.True(t, lu.RunNode.Equal(n2Run))

	// Make sure adding another, lower versioned, node doesn't change the result
	_, err = addNodeToGraphHelper(g, n1Run)
	assert.NoError(t, err)
	lu, err = g.FindBestPkgNode(&pkgjson.PackageVer{Name: "n"})
	assert.NoError(t, err)
	assert.True(t, lu.RunNode.Equal(n2Run))

	// Make sure the newest node gets updated
	_, err = addNodeToGraphHelper(g, n3Run)
	assert.NoError(t, err)
	lu, err = g.FindBestPkgNode(&pkgjson.PackageVer{Name: "n"})
	assert.NoError(t, err)
	assert.True(t, lu.RunNode.Equal(n3Run))
}

// Make sure we can't add a duplicate node
func TestAddDuplicateRunNode(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	_, err = addNodeToGraphHelper(g, pkgARun)
	assert.Error(t, err)
}

// Make sure we can't add a duplicate node
func TestAddDuplicateBuildNode(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	_, err = addNodeToGraphHelper(g, pkgABuild)
	assert.Error(t, err)
}

// Make sure that we can't successfully search when we are missing run nodes
func TestLookupWithoutRunNodes(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, buildNodes)
	assert.Error(t, err)
}

// Add a goal node
func TestAddGoalToEmptyGraph(t *testing.T) {
	g := NewPkgGraph()
	goal, err := g.AddGoalNode("test", nil, false)
	assert.NoError(t, err)
	assert.NotNil(t, goal)
	assert.Equal(t, "test", goal.GoalName)

	goal, err = g.AddGoalNode("test2", nil, true)
	assert.NoError(t, err)
	assert.NotNil(t, goal)
	assert.Equal(t, "test2", goal.GoalName)
}

// Make sure we can't add duplicate goal nodes
func TestDuplicateGoal(t *testing.T) {
	g := NewPkgGraph()
	goal, err := g.AddGoalNode("test", nil, false)
	assert.NoError(t, err)
	assert.NotNil(t, goal)
	assert.Equal(t, "test", goal.GoalName)

	_, err = g.AddGoalNode("test", nil, false)
	assert.Error(t, err)
}

// Search for packages to add to the goal node
func TestGoalWithPackages(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	goal, err := g.AddGoalNode("test", pkgVersions, false)
	assert.NoError(t, err)
	assert.NotNil(t, goal)
	assert.Equal(t, len(allNodes)+1, len(g.AllNodes()))
	goalNodes := graph.NodesOf(g.From(goal.ID()))
	assert.Equal(t, len(runNodes)+len(unresolvedNodes), len(goalNodes))

	goal, err = g.AddGoalNode("test2", []*pkgjson.PackageVer{
		&pkgjson.PackageVer{Name: "A"},
		&pkgjson.PackageVer{Name: "B"},
	}, false)
	assert.NoError(t, err)
	assert.NotNil(t, goal)
	assert.Equal(t, len(allNodes)+2, len(g.AllNodes()))
	goalNodes = graph.NodesOf(g.From(goal.ID()))
	assert.Equal(t, 2, len(goalNodes))
}

// Make sure we fail when trying to add an invalid node to a goal
func TestStrictGoalNodes(t *testing.T) {
	g := NewPkgGraph()
	err := addNodesHelper(g, allNodes)
	assert.NoError(t, err)
	assert.NotNil(t, g)

	_, err = g.AddGoalNode("test", []*pkgjson.PackageVer{&pkgjson.PackageVer{Name: "Not a package"}}, true)
	assert.Error(t, err)
}

// Add a meta node which should link the two disconnected graph components in the test graph
func TestMetaNode(t *testing.T) {
	g, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, g)

	meta1 := g.AddMetaNode([]*PkgNode{}, []*PkgNode{})
	assert.NotNil(t, meta1)

	a, err := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "A"})
	assert.NoError(t, err)
	assert.NotNil(t, a)
	c, err := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "C"})
	assert.NoError(t, err)
	assert.NotNil(t, c)

	meta2 := g.AddMetaNode([]*PkgNode{a.RunNode}, []*PkgNode{c.RunNode})
	assert.NotNil(t, meta2)

	// This should now include the previously disconnected C ver:3-4 tree
	// Total length should now be 15
	//    A tree: len=9
	//    C2 tree: len=5
	//    meta = 1
	component := []*PkgNode{
		pkgARun,
		pkgABuild,
		pkgBRun,
		pkgBBuild,
		pkgCRun,
		pkgCBuild,
		pkgD1Unresolved,
		pkgD2Unresolved,
		pkgD3Unresolved,
		meta2,
		pkgC2Run,
		pkgC2Build,
		pkgD4Unresolved,
		pkgD5Unresolved,
		pkgD6Unresolved,
	}
	for _, mustHave := range component {
		found := false
		for _, n := range g.AllNodesFrom(a.RunNode) {
			found = found || mustHave.Equal(n)
		}
		assert.True(t, found)
	}
	assert.Equal(t, len(component), len(g.AllNodesFrom(a.RunNode)))
}

// Make sure the graph updates after adding meta nodes
func TestMetaNodeAddPkg(t *testing.T) {
	g, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, g)

	a, _ := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "A"})
	c, _ := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "C"})
	meta2 := g.AddMetaNode([]*PkgNode{a.RunNode}, []*PkgNode{c.RunNode})

	component := []*PkgNode{
		pkgARun,
		pkgABuild,
		pkgBRun,
		pkgBBuild,
		pkgCRun,
		pkgCBuild,
		pkgD1Unresolved,
		pkgD2Unresolved,
		pkgD3Unresolved,
		meta2,
		pkgC2Run,
		pkgC2Build,
		pkgD4Unresolved,
		pkgD5Unresolved,
		pkgD6Unresolved,
	}
	for _, mustHave := range component {
		found := false
		for _, n := range g.AllNodesFrom(a.RunNode) {
			found = found || mustHave.Equal(n)
		}
		assert.True(t, found)
	}
	assert.Equal(t, len(component), len(g.AllNodesFrom(a.RunNode)))

	n, err := addNodeToGraphHelper(g, buildUnresolvedNodeHelper(&pkgjson.PackageVer{Name: "test", Version: "99"}))
	assert.NoError(t, err)
	assert.NotNil(t, n)

	err = addEdgeHelper(g, *a.RunNode, *n)
	assert.NoError(t, err)
	assert.Equal(t, 9+5+1+1, len(g.AllNodesFrom(a.RunNode)))
	assert.Equal(t, 5, len(g.AllNodesFrom(c.RunNode)))
}

// Test encoding and decoding a DOT formatted graph
func TestEncodeDecodeDOT(t *testing.T) {

	gOut, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, gOut)

	var buf bytes.Buffer
	err = WriteDOTGraph(gOut, &buf)
	assert.NoError(t, err)

	gIn := NewPkgGraph()
	err = ReadDOTGraph(gIn, &buf)
	assert.NoError(t, err)

	checkTestGraph(t, gIn)
}

// Test the deep copy functionality works as expected.
func TestDeepCopy(t *testing.T) {

	gOut, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, gOut)

	gCopy, err := gOut.DeepCopy()

	checkTestGraph(t, gCopy)
}

// Make sure we can encode and decode repeatedly.
func TestEncodeDecodeMultiDOT(t *testing.T) {

	gOut1, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, gOut1)

	var buf1, buf2 bytes.Buffer
	err = WriteDOTGraph(gOut1, &buf1)
	assert.NoError(t, err)

	gIntermediate := NewPkgGraph()
	err = ReadDOTGraph(gIntermediate, &buf1)
	assert.NoError(t, err)
	err = WriteDOTGraph(gOut1, &buf2)
	assert.NoError(t, err)

	gFinal := NewPkgGraph()
	err = ReadDOTGraph(gFinal, &buf2)

	checkTestGraph(t, gFinal)
}

func TestReadWriteGraph(t *testing.T) {
	gOut, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, gOut)

	_ = os.Remove("test_graph.dot")
	assert.NoError(t, err)
	err = WriteDOTGraphFile(gOut, "test_graph.dot")
	assert.NoError(t, err)

	gIn := NewPkgGraph()
	err = ReadDOTGraphFile(gIn, "test_graph.dot")
	assert.NoError(t, err)
	err = os.Remove("test_graph.dot")
	assert.NoError(t, err)

	checkTestGraph(t, gIn)

	noGraph := NewPkgGraph()
	err = ReadDOTGraphFile(noGraph, "no_such_file.dot")
	assert.Error(t, err)
}

// Validate the reference graph is valid, and that it matches the output of the test graph.
func TestReferenceDOTFile(t *testing.T) {
	gIn := NewPkgGraph()
	err := ReadDOTGraphFile(gIn, "test_graph_reference.dot")
	assert.NoError(t, err)

	checkTestGraph(t, gIn)

	gOut, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, gOut)

	var buf bytes.Buffer
	err = WriteDOTGraph(gOut, &buf)
	assert.NoError(t, err)

	f, err := os.Open("test_graph_reference.dot")
	defer f.Close()
	assert.NoError(t, err)

	// Compare the bytes from the reference file against a fresh encoding
	bytesFromCode, err := ioutil.ReadAll(&buf)
	assert.NoError(t, err)
	bytesFromFile, err := ioutil.ReadAll(f)
	assert.NoError(t, err)
	assert.True(t, len(bytesFromCode) > 0)
	assert.True(t, len(bytesFromFile) > 0)
	assert.Equal(t, 0, bytes.Compare(bytesFromCode, bytesFromFile))
}

// Make sure we can extract a subgraph
func TestSubgraph(t *testing.T) {
	g, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, g)

	root, err := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "B"})
	assert.NoError(t, err)
	subGraph, err := g.CreateSubGraph(root.RunNode)
	assert.NoError(t, err)
	assert.NotNil(t, subGraph)

	component := []*PkgNode{
		pkgBRun,
		pkgBBuild,
		pkgCRun,
		pkgCBuild,
		pkgD2Unresolved,
		pkgD3Unresolved,
	}

	for _, mustHave := range component {
		found := false
		for _, n := range subGraph.AllNodes() {
			found = found || mustHave.Equal(n)
		}
		assert.True(t, found)
	}
	assert.Equal(t, len(component), len(subGraph.AllNodes()))
}

// Make sure we can encode/decode a subgraph
func TestEncodingSubGraph(t *testing.T) {
	g, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, g)

	root, err := g.FindBestPkgNode(&pkgjson.PackageVer{Name: "C", Version: "3-3"})
	assert.NoError(t, err)
	subGraph, err := g.CreateSubGraph(root.RunNode)
	assert.NoError(t, err)
	assert.NotNil(t, subGraph)

	// Copy uses the encode/decode flow
	gCopy, err := subGraph.DeepCopy()

	component := []*PkgNode{
		pkgCRun,
		pkgCBuild,
		pkgD3Unresolved,
	}
	for _, mustHave := range component {
		found := false
		for _, n := range gCopy.AllNodes() {
			found = found || mustHave.Equal(n)
		}
		assert.True(t, found)
	}
	assert.Equal(t, len(component), len(subGraph.AllNodes()))
	assert.Equal(t, len(component), len(gCopy.AllNodes()))
}

func TestShouldSucceedMakeDAGWithGoalNode(t *testing.T) {
	gOut, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, gOut)

	goalNode, err := gOut.AddGoalNode("test", nil, true)
	assert.NotNil(t, goalNode)
	assert.NoError(t, err)

	assert.NoError(t, gOut.MakeDAG())
}

func TestShouldSucceedMakeDAGWithoutGoalNode(t *testing.T) {
	gOut, err := buildTestGraphHelper()
	assert.NoError(t, err)
	assert.NotNil(t, gOut)

	assert.NoError(t, gOut.MakeDAG())
}
