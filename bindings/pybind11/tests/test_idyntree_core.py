"""Tests for idyntree-core Python bindings."""
import itertools
import unittest

import idyntree.pybind as iDynTree
import numpy as np


class IDynTreeRotationTest(unittest.TestCase):

  def test_create_identity(self):
    rotation = iDynTree.Rotation.Identity()
    for r, c in itertools.product(range(3), range(3)):
      if r == c:
        self.assertEqual(rotation[r, c], 1)
      else:
        self.assertEqual(rotation[r, c], 0)

  def test_explicit_constructor(self):
    # Note: the rotation class does not check if the matrix is a real rotation.
    rot_raw = np.arange(9).reshape((3, 3))
    rotation = iDynTree.Rotation(rot_raw[0, 0], rot_raw[0, 1], rot_raw[0, 2],
                                 rot_raw[1, 0], rot_raw[1, 1], rot_raw[1, 2],
                                 rot_raw[2, 0], rot_raw[2, 1], rot_raw[2, 2])
    for r, c in itertools.product(range(3), range(3)):
      self.assertEqual(rotation[r, c], rot_raw[r, c])

  def test_composition(self):
    r1 = iDynTree.Rotation(0, 0, 1,
                           1, 0, 0,
                           0, 1, 0)
    r2 = iDynTree.Rotation(0, -1,  0,
                           0,  0, -1,
                           1,  0,  0)
    r_final = r1 * r2
    r_expected = iDynTree.Rotation(1,  0,  0,
                                   0, -1,  0,
                                   0,  0, -1)
    for r, c in itertools.product(range(3), range(3)):
      self.assertEqual(r_final[r, c], r_expected[r, c])

  def test_inverse(self):
    rotation = iDynTree.Rotation(0, 0, 1,
                                 1, 0, 0,
                                 0, 1, 0)
    exp_rot = iDynTree.Rotation(0, 1, 0,
                                0, 0, 1,
                                1, 0, 0)
    rot_inv = rotation.inverse()
    for r in range(3):
      for c in range(3):
        self.assertAlmostEqual(rot_inv[r, c], exp_rot[r, c])

  def test_position_rotation(self):
    rotation = iDynTree.Rotation(0, 0, 1,
                                 1, 0, 0,
                                 0, 1, 0)
    pos =[0, 0, 1]
    pos_rotated = rotation * pos
    expected_pos = [1, 0, 0]
    for i in range(3):
      self.assertAlmostEqual(pos_rotated[i], expected_pos[i])


class IDynTreeTransformTest(unittest.TestCase):

  def test_creation(self):
    position =[1, 2, 3]
    rotation = iDynTree.Rotation(0, 0, 1,
                                 1, 0, 0,
                                 0, 1, 0)
    transform = iDynTree.Transform(rotation, position)

    # Assert the content is the same.
    for r, c in itertools.product(range(3), range(3)):
      self.assertEqual(transform.rotation[r, c], rotation[r, c])
    for i in range(3):
      self.assertEqual(transform.position[i], position[i])

  def test_identity(self):
    transform = iDynTree.Transform.Identity()
    for i in range(3):
      self.assertEqual(transform.position[i], 0)
    for r, c in itertools.product(range(3), range(3)):
      if r == c:
        self.assertEqual(transform.rotation[r, c], 1)
      else:
        self.assertEqual(transform.rotation[r, c], 0)

  def test_position_transform(self):
    position = [1, 2, 3]
    rotation = iDynTree.Rotation(0, 0, 1,
                                 1, 0, 0,
                                 0, 1, 0)
    transform = iDynTree.Transform(rotation, position)
    pos = [0, 0, 1]
    pos_transformed = transform * pos
    expected_pos = [2, 2, 3]
    for i in range(3):
      self.assertAlmostEqual(pos_transformed[i], expected_pos[i])

  def test_transform_composition(self):
    position = [1, 2, 3]
    rotation = iDynTree.Rotation(0, 0, 1,
                                 1, 0, 0,
                                 0, 1, 0)
    t1 = iDynTree.Transform(rotation, position)
    position = [3, 4, 5]
    rotation = iDynTree.Rotation(0, -1,  0,
                                 0,  0, -1,
                                 1,  0,  0)
    t2 = iDynTree.Transform(rotation, position)
    t_final = t1 * t2
    exp_position = t1.position + t1.rotation * t2.position
    exp_rot = t1.rotation * t2.rotation
    for i in range(3):
      self.assertEqual(t_final.position[i], exp_position[i])
    for r, c in itertools.product(range(3), range(3)):
      self.assertEqual(t_final.rotation[r, c], exp_rot[r, c])


class IDynTreeDirectionTest(unittest.TestCase):

  def test_creation(self):
    n_factor = np.linalg.norm([1, 2, 3])
    raw_dir = [1 / (n_factor), 2 / n_factor, 3 / n_factor]

    direction = raw_dir
    self.assertEqual(list(direction), raw_dir)


class IDynTreeAxisTest(unittest.TestCase):

  def test_read_origin_and_direction_properties(self):
    n_factor = np.linalg.norm([1, 2, 3])
    raw_dir = [1 / (n_factor), 2 / n_factor, 3 / n_factor]
    direction = raw_dir
    origin = [3, 4, 5]
    axis = iDynTree.Axis(direction, origin)
    self.assertEqual(list(axis.direction), raw_dir)
    self.assertEqual(list(axis.origin), [3, 4, 5])


class IDynTreeSpatialInertiaTest(unittest.TestCase):

  def test_creation(self):
    mass = 3.14
    position = [1, 2, 3]
    rotational_inertia = np.zeros((3, 3))
    rotational_inertia[1, 1] = 1

    inertia = iDynTree.SpatialInertia(mass, position, rotational_inertia)
    # Get the matrix (6x6) representation of the inertia.
    matrix = np.array(inertia.as_matrix(), copy=False)
    # The top left 3x3 matrix is a diagonal matrix with the mass on the
    # diagonal.
    for r, c in itertools.product(range(3), range(3)):
      if r == c:
        self.assertEqual(matrix[r, c], mass)
      else:
        self.assertEqual(matrix[r, c], 0)
    # The bottom right 3x3 matrix is the rotational inertia.
    for r, c in itertools.product(range(3), range(3)):
      self.assertEqual(
          matrix[3 + r, 3 + c], rotational_inertia[r, c])
    # The off diagonal 3x3 matrix blocks are m r^ and symmetric.
    def r_vector_item(vector, row, col):
      matrix = np.zeros((3, 3))
      matrix[0, 1] = -vector[2]
      matrix[0, 2] = vector[1]
      matrix[1, 2] = -vector[0]
      matrix[1, 0] = -matrix[0, 1]
      matrix[2, 0] = -matrix[0, 2]
      matrix[2, 1] = -matrix[1, 2]
      return matrix[row, col]

    for r, c in itertools.product(range(3), range(3)):
      r_vector = r_vector_item(position, r, c)
      self.assertEqual(matrix[3 + r, c], r_vector * mass)
      self.assertEqual(matrix[r, 3 + c], -r_vector * mass)

  def test_sum(self):
    mass = 3.14
    position = [1, 2, 3]
    rotational_inertia = np.zeros((3, 3))
    rotational_inertia[1, 1] = 1

    inertia1 = iDynTree.SpatialInertia(mass, position, rotational_inertia)

    mass = 6.28
    position = [4, 5, 6]
    rotational_inertia = np.zeros((3, 3))
    rotational_inertia[2, 2] = 1

    inertia2 = iDynTree.SpatialInertia(mass, position, rotational_inertia)

    # Both inertias are expressed w.r.t. the same frame. We can sum them.
    inertia_sum = inertia1 + inertia2
    # Mass is the sum.
    self.assertAlmostEqual(
        inertia_sum.get_mass(), inertia1.get_mass() + inertia2.get_mass())
    # The first moment of mass is the sum.
    isum_first = self._get_first_moment(inertia_sum)
    isum_first_computed = (
        self._get_first_moment(inertia1) + self._get_first_moment(inertia2))
    for i in range(3):
      self.assertAlmostEqual(isum_first[i], isum_first_computed[i])
    # The rotational inertia is the sum.
    isum_rot = np.array(inertia_sum.get_rotational_inertia_wrt_frame_origin())
    isum_rot_computed = (
        np.array(inertia1.get_rotational_inertia_wrt_frame_origin())
        + np.array(inertia2.get_rotational_inertia_wrt_frame_origin()))
    for r, c in itertools.product(range(3), range(3)):
      self.assertAlmostEqual(isum_rot[r, c], isum_rot_computed[r, c])

  def test_sum_assignment(self):
    # We do not explicitly define this operation.
    # Check if Python does the correct thing by using the elementary + operator.
    mass = 3.14
    position = [1, 2, 3]
    rotational_inertia = np.zeros((3, 3))
    rotational_inertia[1, 1] = 1

    inertia1 = iDynTree.SpatialInertia(mass, position, rotational_inertia)

    mass = 6.28
    position = [4, 5, 6]
    rotational_inertia = np.zeros((3, 3))
    rotational_inertia[2, 2] = 1

    inertia_sum = iDynTree.SpatialInertia(mass, position, rotational_inertia)
    com = self._get_first_moment(inertia_sum)
    rot = inertia_sum.get_rotational_inertia_wrt_frame_origin()

    # Both inertias are expressed w.r.t. the same frame. We can sum them.
    inertia_sum += inertia1
    # Mass is the sum.
    self.assertAlmostEqual(inertia_sum.get_mass(), inertia1.get_mass() + mass)
    # The first moment of mass is the sum.
    isum_first = self._get_first_moment(inertia_sum)
    isum_first_computed = self._get_first_moment(inertia1) + com
    for i in range(3):
      self.assertAlmostEqual(isum_first[i], isum_first_computed[i])
    # The rotational inertia is the sum.
    isum_rot = np.array(inertia_sum.get_rotational_inertia_wrt_frame_origin())
    isum_rot_computed = (
        np.array(inertia1.get_rotational_inertia_wrt_frame_origin()) + rot)
    for r, c in itertools.product(range(3), range(3)):
      self.assertAlmostEqual(isum_rot[r, c], isum_rot_computed[r, c])

  def _get_first_moment(self, inertia: iDynTree.SpatialInertia):
    com = np.array(inertia.get_center_of_mass())
    com *= inertia.get_mass()
    return com


if __name__ == "__main__":
  unittest.main()